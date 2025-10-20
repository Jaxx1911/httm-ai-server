"""Summarize Controller - Business logic for summarization"""

from typing import Dict
from ..models.vit5_model import vit5_model

class SummarizeController:
    """Controller for text summarization operations"""
    
    @staticmethod
    def summarize_text(text: str) -> Dict[str, str]:
        """
        Tóm tắt văn bản
        
        Args:
            text: Văn bản cần tóm tắt
            
        Returns:
            Dict chứa title và summary
        """
        result = vit5_model.summarize_text(text)
        return {
            "title": result["title"],
            "summary": result["summary"]
        }
