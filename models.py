from pydantic import BaseModel
from typing import List, Optional

class Prompt(BaseModel):
    name: str
    description: str
    tags: List[str] = []
    instruction: str
    howto: Optional[str] = None
    author: Optional[str] = None

class SearchPromptsResponse(BaseModel):
    results: List[Prompt]
    nextToken: Optional[str] = None

class ListByNameResponse(BaseModel):
    items: List[Prompt]