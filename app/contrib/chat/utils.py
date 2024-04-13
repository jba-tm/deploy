from typing import Tuple
import requests
from app.conf.config import settings


def retrieve_ai_answer(question: str) -> Tuple[str, bool]:
    try:
        data = {"question": question}
        response = requests.post(
            settings.OPENAI_MODEL_URL,
            headers={"Content-Type": "application/json"},
            json=data
        )
        result = response.json()
        return result.get('text', ""), False
    except Exception as error:
        print(error)
        return str(error), True
