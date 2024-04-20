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
        from pprint import pprint
        status_code = result.get("statusCode", None)
        if status_code == 500:
            return str("Something went wrong!"), True
        return result.get('text', ""), False
    except Exception as error:
        print(error)
        return str(error), True
