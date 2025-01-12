import re
import aiohttp

from async_lru import alru_cache

class LLM:
    """
    model (str) [OPTIONAL]: The model to be used by default. Can be changed afterwards or supercharged upon calling methods.
    url (str) [OPTIONAL]: The URL of the LLM API.
    """
    def __init__(self, model: str = "llama3.2:1b", url: str = "http://127.0.0.1:11434/api/chat"):
        self.model = model
        self.url = url

    """Prompt the a model with a custom prompt.
    
    prompt (str): The prompt to send to the model.
    system_context (str): The text to stand in system context window.
    model (str | None): The name of the model to query. If unset, will default to the class property `model`.
    
    raises ValueError: HTTP request failed
    
    returns (str): The model output
    """
    @alru_cache(9999)
    async def prompt(self, prompt: str, system_context: str = "", model: str | None = None) -> str:
        if not model:
            model = self.model # Default to the model set by the constructor
        data = {
            "model": model,
            "messages": [
                {
                "role": "user",
                "content": prompt,
                },
                {
                "role": "system",
                "content": system_context,
                },
            ],
            "stream": False, # Response in a single JSON
            "options": {
                "seed": 1, # Reproducible outputs for similar inputs
                "temperature": 0.25, # Not too creative
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=data) as response:
                print(await response.text())
                if response.status == 200:
                    output_data = await response.json()
                    message: dict[str, str] = output_data.get("message")
                    if not message: return ""
                    output = message.get("content", "")
                    # Clean output
                    output = output.removeprefix("\u003c|start_header_id|\u003eassistant\u003c|end_header_id|\u003e").strip()
                    # output = re.sub(r"\n.*", "", output)
                    output = output.strip("\"\'").strip()
                    return output
        
                else: raise ValueError(f"Error {response.status}: {await response.text()}")