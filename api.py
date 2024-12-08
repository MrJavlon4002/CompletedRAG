from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from bot import ask_question

app = FastAPI()

class QuestionRequest(BaseModel):
    session_id: str
    query: str

@app.post("/ask")
async def ask_question_endpoint(request: QuestionRequest) -> Dict[str, str]:
    session_id = request.session_id
    user_input = request.query
    try:
        answer = ask_question(session_id = session_id, user_input = user_input)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)