import os
import re
from typing import List, Dict, Optional
from models import Prompt

class PromptLoader:
    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir
        self._prompts_cache = None
    
    def _parse_markdown_file(self, file_path: str) -> Optional[Prompt]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use filename without extension as name
            name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Extract description (first paragraph after title)
            lines = content.split('\n')
            description = ""
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    # Find next non-empty line after title
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith('#'):
                            description = lines[j].strip()
                            break
                    break
            
            # Use full content as instruction
            instruction = content
            
            # Extract tags from filename or content patterns
            tags = []
            if 'file' in name.lower():
                tags.append('file')
            if 'analysis' in name.lower() or 'analyze' in name.lower():
                tags.append('analysis')
            if 'format' in name.lower():
                tags.append('formatting')
            
            return Prompt(
                name=name,
                description=description or name,
                tags=tags,
                instruction=instruction,
                author="Custom"
            )
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def load_prompts(self) -> List[Prompt]:
        if self._prompts_cache is not None:
            return self._prompts_cache
        
        prompts = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(self.prompts_dir, filename)
                prompt = self._parse_markdown_file(file_path)
                if prompt:
                    prompts.append(prompt)
        
        self._prompts_cache = prompts
        return prompts
    
    def search_prompts(self, tags: Optional[List[str]] = None) -> List[Prompt]:
        prompts = self.load_prompts()
        
        if not tags:
            return prompts
        
        filtered = []
        for prompt in prompts:
            if any(tag.lower() in [t.lower() for t in prompt.tags] for tag in tags):
                filtered.append(prompt)
        
        return filtered
    
    def get_prompt_by_name(self, name: str) -> Optional[Prompt]:
        prompts = self.load_prompts()
        
        for prompt in prompts:
            if prompt.name.lower() == name.lower():
                return prompt
        
        return None