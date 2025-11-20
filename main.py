from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import os
from models import SearchPromptsResponse, ListByNameResponse
from prompt_loader import PromptLoader

app = FastAPI(title="Custom Promptz API", version="1.0.0")

# Initialize prompt loader

#Working
#PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompt-library", "prompts")
#Working for outside the above folder too.
#PROMPTS_DIR = "C:\\Users\\User1\\projects\\mcp_server\\promptz-dev\\prompt-library\\prompts"
prompt_loader = PromptLoader("C:\\Users\\User1\\Project\\DEMO\\mcp\\prompt-library\\prompts")

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