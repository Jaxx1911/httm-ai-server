from nltk.corpus.reader import titles
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.repositories.model_repository import ModelRepository


class SummarizeService:
    def __init__(self, model_repository : ModelRepository):
        self.model_repository = model_repository

    def summarize(self, text):
        model = self.model_repository.get_active_model()

        tokenizer = AutoTokenizer.from_pretrained(model.model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model.model_path)

        title, summary = self.generate_summary(text, tokenizer, model)

        return {
            "title": title,
            "summary": summary,
            "model_version": model.version
        }

    def generate_summary(self, text, tokenizer, model):
        inputs = tokenizer(
            text,
            max_length=512,
            truncation=True,
            truncate=True,
            return_tensors="pt"
        )

        titles = model.generate(
            **inputs,
            max_length=150,
            num_beams=4,
            early_stopping=True
        )

        title = tokenizer.decode(titles[0], skip_special_tokens=True)

        summary_ids = model.generate(
            **inputs,
            max_new_tokens=150,
            num_beams=4,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return title, summary
