from llama_index.llms.openai import OpenAI
from llama_index.llms.mistralai import MistralAI
from llama_index.llms.gemini import Gemini
from llama_index.llms.ollama import Ollama


def init_llm_agent(api,
                   model, 
                   max_tokens, 
                   max_retries, 
                   timeout, 
                   api_key,
                   system_prompt):
    

    if(api=="openai"):
        
        return OpenAI(model=model, 
                    max_tokens=max_tokens, 
                    max_retries=max_retries,
                    timeout=timeout,
                    api_key=api_key,
                    system_prompt=system_prompt)
    
    elif(api=="mistral"):

        return MistralAI(model=model, 
                    max_tokens=max_tokens, 
                    max_retries=max_retries,
                    timeout=timeout,
                    api_key=api_key,
                    system_prompt=system_prompt)
    

    elif(api=="gemini"):

        return Gemini(model=model, 
                    max_tokens=max_tokens, 
                    max_retries=max_retries,
                    timeout=timeout,
                    api_key=api_key,
                    system_prompt=system_prompt)
    

    elif(api=="ollama"):

        return Ollama(model=model, 
                    max_tokens=max_tokens, 
                    max_retries=max_retries,
                    timeout=timeout,
                    api_key=api_key,
                    system_prompt=system_prompt)
    
    else:

        raise ValueError(f"The {model} initialization is not implemented yet. The available LLMs are : \
                         'openai', 'mistral'")