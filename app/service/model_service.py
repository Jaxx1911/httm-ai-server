import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer
from typing import Dict, Optional
from rouge_score import rouge_scorer

from constant.constants import default_training_args
from repositories.model_repository import ModelRepository
from schemas.schema import TrainRequest, ModelMetrics
import logging
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self, repository: ModelRepository):
        self.repository = repository
        self.model_base_path = "./models_versions"
        os.makedirs(self.model_base_path, exist_ok=True)

    @staticmethod
    def compute_metrics(model, tokenizer, eval_dataset) -> Dict:
        """Compute accuracy, precision, recall, and F1 score for the model"""
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

        # Calculate ROUGE scores as proxy for metrics
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_scores = []

        for pred, ref in zip(predictions, references):
            scores = scorer.score(ref, pred)
            rouge_scores.append(scores)

        # Calculate average ROUGE-L F1 score
        rouge_l_f1 = np.mean([score['rougeL'].fmeasure for score in rouge_scores])
        rouge_l_precision = np.mean([score['rougeL'].precision for score in rouge_scores])
        rouge_l_recall = np.mean([score['rougeL'].recall for score in rouge_scores])

        # For summarization tasks, we use ROUGE metrics as our evaluation
        metrics = {
            "accuracy": float(rouge_l_f1),
            "precision": float(rouge_l_precision),
            "recall": float(rouge_l_recall),
            "f1_score": float(rouge_l_f1)
        }

        logger.info(f"Metrics computed - Accuracy: {metrics['accuracy']:.4f}, "
                   f"Precision: {metrics['precision']:.4f}, "
                   f"Recall: {metrics['recall']:.4f}, "
                   f"F1: {metrics['f1_score']:.4f}")

        return metrics

    def train_model(self, train_request: TrainRequest) -> Dict:
        """Train or retrain a ViT5 model"""
        logger.info(f"Starting training for version: {train_request.version}")

        # Load base model if retraining
        model_name = "VietAI/vit5-base"
        if train_request.is_retrain and train_request.base_version_id is not None:
            base_model = self.repository.get_model_version_by_id(train_request.base_version_id)
            if not base_model:
                raise ValueError(f"Base model version {train_request.base_version_id} not found for retraining.")
            logger.info(f"Retraining from base model version: {train_request.base_version_id}")
            model_name = base_model.model_path

        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # Load dataset
        dataset = load_dataset("json", data_files={"train": train_request.train_data_path})["train"]

        # Split dataset into train and eval
        split_dataset = dataset.train_test_split(test_size=0.1)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]

        # Tiền xử lý dữ liệu
        def preprocess(examples):
            inputs = examples['text']
            model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")

            with tokenizer.as_target_tokenizer():
                labels = tokenizer(examples['summary'], max_length=150, truncation=True, padding="max_length")

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

        # Generate version name
        version = train_request.version

        # Save model
        model_save_path = os.path.join(self.model_base_path, f"model_{version}")
        os.makedirs(model_save_path, exist_ok=True)
        trainer.save_model(model_save_path)
        tokenizer.save_pretrained(model_save_path)
        logger.info(f"Model saved to {model_save_path}")

        # Compute metrics after training
        logger.info("Computing metrics on evaluation dataset...")
        metrics = self.compute_metrics(model, tokenizer, tokenized_eval)

        # Save to database
        model_version = self.repository.create_model_version(
            version=version,
            model_path=model_save_path,
            accuracy=metrics["accuracy"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
        )

        # Set as active if it's the first model
        all_models = self.repository.get_all_model_versions()
        if len(all_models) == 1:
            self.repository.set_active_model(version)
            logger.info(f"Model {version} set as active (first model)")

        logger.info(f"Training completed for version: {version}")

        return {
            "version": version,
            "model_path": model_save_path,
            "metrics": ModelMetrics(**metrics),
            "message": "Model trained successfully"
        }

    def get_active_model_info(self) -> Optional[Dict]:
        """Get information about the active model"""
        active_model = self.repository.get_active_model()
        if not active_model:
            return None

        return {
            "version": active_model.version,
            "model_path": active_model.model_path,
            "accuracy": active_model.accuracy,
            "precision": active_model.precision,
            "recall": active_model.recall,
            "f1_score": active_model.f1_score
        }

    def activate_model_version(self, version: str) -> bool:
        """Activate a specific model version"""
        model = self.repository.set_active_model(version)
        return model is not None

