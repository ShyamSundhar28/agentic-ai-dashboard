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

    def infer_column_name(self, current_name: str, samples: list) -> str:
        """
        Uses the LLM to guess a proper column name based on its data samples.
        """
        if not settings.google_api_key:
            return f"{current_name}_inferred"
            
        prompt = f"""
        You are a data engineering assistant. I have a column in a CSV dataset with a bad or missing header name: "{current_name}".
        Here are the first few rows of data from this column:
        {samples}
        
        Please reply with ONLY a single, short, concise, snake_case string representing the best column name for this data. Do not include quotes or explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            new_name = response.text.strip().lower()
            # Clean up the response just in case the LLM adds markdown or spaces
            import re
            new_name = re.sub(r'[^a-z0-9_]', '', new_name.replace(' ', '_'))
            return new_name if new_name else current_name
        except Exception as e:
            return current_name
