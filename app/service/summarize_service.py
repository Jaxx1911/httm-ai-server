class SummarizeService:
    def __init__(self):
        pass

    def summarize(self, text):
        return {
            "original_text": text,
            "title": "Sample Title",
            "summary": "This is a sample summary generated for the provided text.",
            "model_version": "v1.0.0"
        }