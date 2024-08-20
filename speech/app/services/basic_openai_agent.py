import os

from dotenv import load_dotenv
from fastapi import Depends
from pydantic import BaseModel

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')


class EventInfo(BaseModel):
    title: str
    description: str


class OpenAIModelClient:
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    async def generate_from_abstract(self, abstract: str) -> EventInfo:
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一個優秀的演講行銷人員，根據講者提供的一句關於內容的總結，你能想出讓人無法拒絕的標題(Title)，以及引人入勝的描述(Description)，\
                內容發想方向包括：一句話總結講者的內容，講者有趣的引言，並且避免生成對進行方式，禁止輸出對受眾的描述\
                ，並且將結果使用這樣的方式輸出 {\"Title\": 標題內容, \"Description\": 內容描述}"},
                {"role": "user", "content": abstract},
            ],
            response_format=EventInfo,
        )

        return completion.choices[0].message.parsed


def get_openai_agent() -> OpenAIModelClient:
    return OpenAIModelClient(openai_api_key)


OpenAIClientDependency = Depends(get_openai_agent)
