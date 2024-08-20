import openai
from typing import Dict

class BasicOpenAIAgent:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def process(self, messages: list[Dict[str, str]]) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error processing input: {str(e)}"

    def change_model(self, new_model: str):
        self.model = new_model

    def simple_query(self, prompt: str) -> str:
        return self.process([{"role": "user", "content": prompt}])