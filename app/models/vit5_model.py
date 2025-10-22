# """ViT5 Model for text summarization"""

# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments
# from datasets import Dataset
# import torch
# import datetime
# from typing import List, Dict, Any
# from rouge_score import rouge_scorer
# import numpy as np
# from ..config.settings import settings

# class ViT5Model:
#     def __init__(self, model_name: str = None):
#         """
#         Khởi tạo model ViT5 cho tóm tắt văn bản
#         """
#         self.model_name = model_name or settings.MODEL_NAME
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
#         self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.model.to(self.device)
    
#     def train_model(self, train_data: List[Dict[str, str]], parameters: Dict[str, Any]):
#         """
#         Train hoặc re-train model ViT5 với dữ liệu được cung cấp
        
#         Args:
#             train_data: List các dict chứa 'input_text' và 'target_text'
#             parameters: Dict chứa các thông số train (learning_rate, epochs, batch_size, etc.)
        
#         Returns:
#             Dict chứa kết quả train và metrics đánh giá
#         """
#         # Chia dữ liệu train/validation
#         split_idx = int(len(train_data) * settings.TRAIN_VAL_SPLIT)
#         train_split = train_data[:split_idx]
#         val_split = train_data[split_idx:]
        
#         # Chuẩn bị dữ liệu
#         train_dataset = Dataset.from_list(train_split)
#         val_dataset = Dataset.from_list(val_split) if val_split else None
        
#         def preprocess_function(examples):
#             inputs = self.tokenizer(
#                 examples['input_text'], 
#                 max_length=512, 
#                 truncation=True, 
#                 padding='max_length'
#             )
#             targets = self.tokenizer(
#                 examples['target_text'], 
#                 max_length=128, 
#                 truncation=True, 
#                 padding='max_length'
#             )
#             inputs['labels'] = targets['input_ids']
#             return inputs
        
#         tokenized_train = train_dataset.map(preprocess_function, batched=True)
#         tokenized_val = val_dataset.map(preprocess_function, batched=True) if val_dataset else None
        
#         # Thiết lập training arguments
#         training_args = TrainingArguments(
#             output_dir=settings.MODEL_CHECKPOINT_DIR,
#             learning_rate=parameters.get('learning_rate', settings.DEFAULT_LEARNING_RATE),
#             num_train_epochs=parameters.get('epochs', settings.DEFAULT_EPOCHS),
#             per_device_train_batch_size=parameters.get('batch_size', settings.DEFAULT_BATCH_SIZE),
#             per_device_eval_batch_size=parameters.get('batch_size', settings.DEFAULT_BATCH_SIZE),
#             save_steps=parameters.get('save_steps', 500),
#             save_total_limit=2,
#             logging_dir=settings.LOGS_DIR,
#             logging_steps=100,
#             evaluation_strategy="epoch" if val_dataset else "no",
#         )
        
#         # Khởi tạo Trainer
#         trainer = Trainer(
#             model=self.model,
#             args=training_args,
#             train_dataset=tokenized_train,
#             eval_dataset=tokenized_val,
#         )
        
#         # Train model
#         start_time = datetime.datetime.now()
#         train_result = trainer.train()
#         end_time = datetime.datetime.now()
        
#         # Lưu model đã train
#         self.model.save_pretrained(settings.TRAINED_MODEL_DIR)
#         self.tokenizer.save_pretrained(settings.TRAINED_MODEL_DIR)
        
#         # Đánh giá model trên validation set
#         metrics = {}
#         if val_split:
#             metrics = self.evaluate_model(val_split)
        
#         # Trả về kết quả
#         result = {
#             "train_loss": train_result.training_loss,
#             "train_runtime": str(end_time - start_time),
#             "samples": len(train_data),
#             "validation_samples": len(val_split) if val_split else 0,
#             "model_path": settings.TRAINED_MODEL_DIR,
#             "metrics": metrics
#         }
        
#         return result
    
#     def evaluate_model(self, eval_data: List[Dict[str, str]]) -> Dict[str, float]:
#         """
#         Đánh giá model với dữ liệu validation
#         Tính các metrics: accuracy, precision, recall, f1, ROUGE scores
        
#         Args:
#             eval_data: List các dict chứa 'input_text' và 'target_text'
        
#         Returns:
#             Dict chứa các metrics đánh giá
#         """
#         predictions = []
#         references = []
        
#         # Sinh predictions cho tất cả samples
#         for item in eval_data:
#             result = self.summarize_text(item['input_text'])
#             predictions.append(result['summary'])
#             references.append(item['target_text'])
        
#         # Tính ROUGE scores
#         scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
#         rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
        
#         for pred, ref in zip(predictions, references):
#             scores = scorer.score(ref, pred)
#             rouge_scores['rouge1'].append(scores['rouge1'].fmeasure)
#             rouge_scores['rouge2'].append(scores['rouge2'].fmeasure)
#             rouge_scores['rougeL'].append(scores['rougeL'].fmeasure)
        
#         # Tính trung bình ROUGE scores
#         avg_rouge1 = np.mean(rouge_scores['rouge1'])
#         avg_rouge2 = np.mean(rouge_scores['rouge2'])
#         avg_rougeL = np.mean(rouge_scores['rougeL'])
        
#         # Tính F1 score dựa trên ROUGE-L (metric phổ biến cho text summarization)
#         f1_score = avg_rougeL
        
#         metrics = {
#             "accuracy": float(avg_rouge1),      # ROUGE-1 F1 (unigram overlap)
#             "precision": float(avg_rouge2),     # ROUGE-2 F1 (bigram precision)
#             "recall": float(avg_rougeL),        # ROUGE-L F1 (subsequence recall)
#             "f1_score": float(f1_score),        # ROUGE-L F1 (overall)
#             "rouge1_f1": float(avg_rouge1),
#             "rouge2_f1": float(avg_rouge2),
#             "rougeL_f1": float(avg_rougeL),
#         }
        
#         return metrics
    
#     def summarize_text(self, text: str, max_length: int = None) -> Dict[str, str]:
#         """
#         Tóm tắt văn bản và sinh tiêu đề
        
#         Args:
#             text: Văn bản cần tóm tắt
#             max_length: Độ dài tối đa của tóm tắt
        
#         Returns:
#             Dict chứa 'title' và 'summary'
#         """
#         if max_length is None:
#             max_length = settings.MAX_SUMMARY_LENGTH
            
#         # Sinh tóm tắt
#         summary_input = f"summarize: {text}"
#         summary_inputs = self.tokenizer(
#             summary_input, 
#             return_tensors="pt", 
#             max_length=512, 
#             truncation=True
#         ).to(self.device)
        
#         summary_outputs = self.model.generate(
#             summary_inputs['input_ids'],
#             max_length=max_length,
#             num_beams=4,
#             early_stopping=True
#         )
#         summary = self.tokenizer.decode(summary_outputs[0], skip_special_tokens=True)
        
#         # Sinh tiêu đề (title)
#         title_input = f"title: {text}"
#         title_inputs = self.tokenizer(
#             title_input, 
#             return_tensors="pt", 
#             max_length=512, 
#             truncation=True
#         ).to(self.device)
        
#         title_outputs = self.model.generate(
#             title_inputs['input_ids'],
#             max_length=settings.MAX_TITLE_LENGTH,
#             num_beams=4,
#             early_stopping=True
#         )
#         title = self.tokenizer.decode(title_outputs[0], skip_special_tokens=True)
        
#         return {
#             "title": title,
#             "summary": summary
#         }

# # Khởi tạo model global
# vit5_model = ViT5Model()
