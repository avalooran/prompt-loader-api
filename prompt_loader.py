import os
import re
import requests
from typing import List, Dict, Optional
from models import Prompt

class PromptLoader:
    branch = "prompt_poc"
    
    def __init__(self, github_repo: str, github_token: Optional[str] = None):
        self.github_repo = github_repo  # format: "owner/repo" or "owner/repo/path/to/prompts"
        self.github_token = github_token
        self._prompts_cache = None
        self.base_url = "https://api.github.com/repos"
    
    def _parse_markdown_content(self, filename: str, content: str) -> Optional[Prompt]:
        try:
            # Use filename without extension as name
            name = os.path.splitext(filename)[0]
            
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
            print(f"Error parsing {filename}: {e}")
            return None
    
    def _get_github_files(self) -> List[Dict]:
        parts = self.github_repo.split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repo format. Use 'owner/repo' or 'owner/repo/path'")
        
        owner, repo = parts[0], parts[1]
        path = '/'.join(parts[2:]) if len(parts) > 2 else ''
        
        url = f"{self.base_url}/{owner}/{repo}/contents/{path}"
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        params = {'ref': self.branch}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def load_prompts(self) -> List[Prompt]:
        if self._prompts_cache is not None:
            return self._prompts_cache
        
        prompts = []
        files = self._get_github_files()
        
        for file_info in files:
            if file_info['name'].endswith('.md') and file_info['type'] == 'file':
                # Get file content
                content_response = requests.get(file_info['download_url'])
                content_response.raise_for_status()
                content = content_response.text
                
                prompt = self._parse_markdown_content(file_info['name'], content)
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