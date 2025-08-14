from fastapi import FastAPI
from dotenv import load_dotenv
import os
import cohere
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

conversation_history = {}


@app.get("/")
def get_root():
    return {"message": "Hello world"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"hello {name}"}


class Query(BaseModel):
    userid: str
    message: str


@app.post("/chat/")
def chat(query: Query):
    if query.userid not in conversation_history:
        conversation_history[query.userid] = []
    conversation_history[query.userid].append(
        {"role": "USER", "message": query.message}
    )
    history_messages = [
        {"role": "USER" if m["role"] == "USER" else "CHATBOT", "message": m["message"]}
        for m in conversation_history[query.userid]
    ]
    response = co.chat(
        model="command-r-plus",
        message=query.message,
        chat_history=history_messages[:-1],
    )
    conversation_history[query.userid].append(
        {"role": "CHATBOT", "message": response.text}
    )
    return {
        "user": query.userid,
        "reply": response.text,
        "history": conversation_history[query.userid],
    }


if __name__ == "__main__":
    test = co.chat(
        model="command-r-plus", message="What are some fun things to do in New York?"
    )
    print(test.text)
