from fastapi import FastAPI
from pydantic import BaseModel
from utils import load_documents, search_documents

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

documents = load_documents()

@app.post("/api/")
def ask_question(req: QueryRequest):
    question = req.question.strip()
    answer, links = search_documents(question, documents)
    return {
        "answer": answer,
        "links": links
    }
