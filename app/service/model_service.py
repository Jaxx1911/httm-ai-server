from datetime import datetime
import json
import os
import random

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer
from typing import Dict, Optional
from rouge_score import rouge_scorer

from app.models.database import Model
from app.repositories.sample_repository import SampleRepository
from app.schemas.model_schemas import ModelVersionResponse
from constant.constants import default_training_args
from app.repositories.model_repository import ModelRepository
from app.schemas import TrainRequest, ModelMetrics
import logging
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self, repository: ModelRepository, sample_repository: SampleRepository):
        self.repository = repository
        self.sample_repository = sample_repository
        self.model_base_path = "./models_versions"
        os.makedirs(self.model_base_path, exist_ok=True)

    @staticmethod
    def compute_metrics(model, tokenizer, eval_dataset) -> Dict:
        logger.info("Computing metrics...")
        model.eval()
        predictions = []
        references = []
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        
        # Generate predictions for eval dataset
        for i in range(len(eval_dataset)):
            example = eval_dataset[i]
            input_ids = torch.tensor([example['input_ids']]).to(device)
            attention_mask = torch.tensor([example['attention_mask']]).to(device)
            
            with torch.no_grad():
                outputs = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_length=150,
                    num_beams=4,
                    early_stopping=True
                )
            
            pred_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            ref_text = tokenizer.decode(example['labels'], skip_special_tokens=True)
            predictions.append(pred_text)
            references.append(ref_text)
        
        # Calculate ROUGE scores
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_scores = []
        for pred, ref in zip(predictions, references):
            scores = scorer.score(ref, pred)
            rouge_scores.append(scores)
        
        # Calculate average ROUGE-L scores
        rouge_1_f1 = np.mean([score['rouge1'].fmeasure for score in rouge_scores])
        rouge_l_f1 = np.mean([score['rougeL'].fmeasure for score in rouge_scores])
        rouge_l_precision = np.mean([score['rougeL'].precision for score in rouge_scores])
        rouge_l_recall = np.mean([score['rougeL'].recall for score in rouge_scores])
        
        # Metrics
        metrics = {
            "accuracy": float(rouge_1_f1),         
            "f1_score": float(rouge_l_f1),
            "precision": float(rouge_l_precision),
            "recall": float(rouge_l_recall),
        }

        logger.info(f"Metrics computed - Accuracy: {metrics['accuracy']:.4f}, "
                   f"Precision: {metrics['precision']:.4f}, "
                   f"Recall: {metrics['recall']:.4f}, "
                   f"F1: {metrics['f1_score']:.4f}")

        return metrics

    def train_model(self, train_request: TrainRequest) -> Dict:
        model_name = "VietAI/vit5-base"

        version = 1
        base_model = None
        if train_request.is_retrain:
            base_model = self.repository.get_by_id(train_request.id)
            if not base_model:
                raise ValueError(f"Base model {train_request.id} not found for retraining.")
    
            version = base_model.version + 1
            model_name = base_model.model_path
            logger.info(f"Retraining model version: {train_request.id}, new version: {version}")

        # Load base model
        elif train_request.base_model_id is not None and train_request.base_model_id != "":
            base_model = self.repository.get_by_id(train_request.base_model_id)
            if not base_model:
                raise ValueError(f"Base model {train_request.base_model_id} not found for training.")
            logger.info(f"Training from base model: {train_request.base_model_id}")
            model_name = base_model.model_path

        

        logger.info(f"Starting traininG")

        # Load tokenizer và model model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


        dataset_file_path = self.build_dataset_from_samples(train_request.sample_ids, is_select_all=train_request.is_select_all)

        dataset = load_dataset("json", data_files={"train": dataset_file_path})["train"]

        #chia dataset thành tập train, eval
        split_dataset = dataset.train_test_split(test_size=0.1)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]

        # hàm tiền xử lý dữ liệu
        def preprocess(examples):
            inputs = examples['text']
            model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")

            with tokenizer.as_target_tokenizer():
                labels = tokenizer(examples['target'], max_length=256, truncation=True, padding="max_length")

            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        tokenized_train = train_dataset.map(preprocess, batched=True)
        tokenized_eval = eval_dataset.map(preprocess, batched=True)

        # Training
        trainer = Trainer(
            model=model,
            args=default_training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_eval,
        )

        logger.info("Starting training...")
        trainer.train()
        logger.info("Training completed. Saving model...")

        # Save model vào server
        model_save_path = os.path.join(self.model_base_path, f"model_{train_request.model_name}_{version}")
        os.makedirs(model_save_path, exist_ok=True)
        trainer.save_model(model_save_path)
        tokenizer.save_pretrained(model_save_path)
        logger.info(f"Model saved to {model_save_path}")

        # tính metrics
        logger.info("Computing metrics on evaluation dataset...")
        metrics = self.compute_metrics(model, tokenizer, tokenized_eval)

        logger.info(f"Training completed for version: {version}")
        # clear file dataset tạm
        os.remove(dataset_file_path)
        if not train_request.is_retrain:
            return ModelVersionResponse(
                id=None,
                version=str(version),
                name=train_request.model_name,
                accuracy=metrics["accuracy"],
                precision=metrics["precision"],
                recall=metrics["recall"],
                f1_score=metrics["f1_score"],
                model_path=model_save_path,
                status="completed",
                base_model_id=None,
                sample_ids=train_request.sample_ids,
                is_select_all=train_request.is_select_all,
                is_retrain=False
            )
        else:
            return ModelVersionResponse(
                id=base_model.id,
                version=str(version),
                name=base_model.model_name,
                accuracy=metrics["accuracy"],
                precision=metrics["precision"],
                recall=metrics["recall"],
                f1_score=metrics["f1_score"],
                model_path=model_save_path,
                status="completed",
                base_model_id=base_model.base_model_id,
                sample_ids=train_request.sample_ids,
                is_select_all=train_request.is_select_all,
                is_retrain=True
            )

        # # set active nếu là model đầu tiên
        # all_models = self.repository.get_all()
        # if len(all_models) == 1:
        #     self.repository.set_active(all_models[0])
        #     logger.info(f"Model {version} set as active (first model)")

        

        return {
            "id": model_version.id,
            "version": version,
            "model_path": model_save_path,
            "metrics": ModelMetrics(**metrics),
            "message": "Model trained successfully"
        }
    
    def get_models(self):
        """Get all model versions"""
        return self.repository.get_all()

    def activate_model(self, model_id: str) -> bool:
        model = self.repository.get_by_id(model_id)
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")
        
        self.repository.set_active(model)
        return True

    def build_dataset_from_samples(self, sample_ids: list[str], is_select_all: bool) -> str:
        sample = []
        if is_select_all:
            samples = self.sample_repository.get_if_not_in_ids(sample_ids)
        else:
            samples = self.sample_repository.get_by_ids(sample_ids)
        dataset_path = f"./temp_dataset_{random.randint(1000, 9999)}.json"


        with open(dataset_path, "w", encoding="utf-8") as f:
            for sample in samples:
                record1 = {
                    "text": f"title: {sample.input_text}",
                    "target": sample.title,
                }
                record2 = {
                    "text": f"summarize: {sample.input_text}",
                    "target": sample.target_summary,
                }
                f.write(json.dumps(record1, ensure_ascii=False) + "\n")
                f.write(json.dumps(record2, ensure_ascii=False) + "\n")

        return dataset_path

    def save_model(self, model_data: dict) -> bool:
        if not model_data.get("is_retrain"):
            model_version = self.repository.insert(
                Model(
                    version=model_data.get("version"),
                    name=f"ViT5 Model {model_data.get('name')}",
                    model_path=model_data.get("model_path"),
                    accuracy=model_data.get("accuracy"),
                    precision=model_data.get("precision"),
                    recall=model_data.get("recall"),
                    f1_score=model_data.get("f1_score"),
                    status="completed",
                    is_active=False,
                    base_model_id=model_data.get("base_model_id"),
                    created_at=datetime.now(),
                    created_by="admin1"
                ), model_data.get("sample_ids"), is_select_all=model_data.get("is_select_all")
            )
        else:
            base_model = self.repository.get_by_id(model_data.get("id"))
            base_model.version = model_data.get("version")
            base_model.model_path = model_data.get("model_path")
            base_model.accuracy = model_data.get("accuracy")
            base_model.precision = model_data.get("precision")
            base_model.recall = model_data.get("recall")
            base_model.f1_score = model_data.get("f1_score")
            base_model.status = "completed"
            base_model.created_at = datetime.now()

            model_version = self.repository.update(
                base_model, model_data.get("sample_ids"), is_select_all=model_data.get("is_select_all")
            )
        return True
