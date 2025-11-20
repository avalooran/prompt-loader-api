from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import os
from models import SearchPromptsResponse, ListByNameResponse
from prompt_loader import PromptLoader

app = FastAPI(title="Custom Promptz API", version="1.0.0")

# Initialize prompt loader with GitHub repo
prompt_loader = PromptLoader("avalooran/prompt-library/welog")  # Replace with actual GitHub repo

@app.get("/")
def read_root():
    return {"message": "Custom Promptz API", "version": "1.0.0"}

@app.get("/search-prompts", response_model=SearchPromptsResponse)
def search_prompts(
    tags: Optional[List[str]] = Query(None),
    nextToken: Optional[str] = Query(None)
):
    try:
        prompts = prompt_loader.search_prompts(tags)
        return SearchPromptsResponse(results=prompts, nextToken=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-by-name", response_model=ListByNameResponse)
def list_by_name(name: str = Query(...)):
    try:
        prompt = prompt_loader.get_prompt_by_name(name)
        if not prompt:
            return ListByNameResponse(items=[])
        return ListByNameResponse(items=[prompt])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)