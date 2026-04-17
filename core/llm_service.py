import google.generativeai as genai
import os
from core.config import settings

class LLMService:
    def __init__(self):
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def summarize_findings(self, context: str) -> str:
        """
        Generates a natural language narrative from technical data using Gemini.
        """
        if not settings.google_api_key:
            return "Narrative insights unavailable (Google API Key not found)."

        prompt = f"""
        You are a business intelligence assistant. 
        Your goal is to provide a concise, high-level summary of the following data findings.
        Keep it professional, actionable, and data-driven.
        
        Findings:
        {context}
        
        Summary:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Narrative insights unavailable due to error: {str(e)}"
