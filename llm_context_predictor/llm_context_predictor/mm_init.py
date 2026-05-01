from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.multi_modal_llms.mistralai import MistralAIMultiModal
from llama_index.multi_modal_llms.gemini import GeminiMultiModal
from llama_index.multi_modal_llms.ollama import OllamaMultiModal
from llm_context_predictor.utils import _safe_parse

def init_multimodal_llm(api,
                       model, 
                       max_new_tokens, 
                       context_window, 
                       image_detail, 
                       max_retries, 
                       timeout, 
                       api_key):
    
    '''
    This function initializes the multimodal AI for different APIs such as OpenAI, Mistral, etc. 

    Available APIs: "openai", "mistral"

    Parameters:

        api: str
            Specifies which API to use (e.g., "openai", "mistral", etc.).

        model: str
            The specific model name or version to initialize (e.g., "gpt-4", "mistral-7b"). 

        max_new_tokens: int
            The maximum numbers of tokens to generate, ignoring the number of tokens in the prompt 

        context_window: int
            The maximum number of context tokens for the model. 

        image_detail: str
            Determines the level of detail for image generation or processing (e.g., "low", "medium", "high"). 

        max_retries: int
            Indicates the maximum number of retries allowed in case of API request failures.

        timeout: int
            Sets the timeout duration (in seconds) for API requests. 

        api_key: str
            The API key required for authenticating with the selected service. 

    Returns:
        MultimodelAI() instance

    Example:
        init_multimodal_ai(api="openai", 
                           model="gpt-4", 
                           max_new_tokens=100, 
                           context_window=4096, 
                           image_detail="high", 
                           max_retries=3, 
                           timeout=30, 
                           api_key="your_api_key_here")
    '''
    if(api=="openai"):

        return OpenAIMultiModal(model=model, 
                                    max_new_tokens=max_new_tokens, 
                                    context_window = context_window,
                                    image_detail= image_detail,
                                    max_retries=max_retries,
                                    timeout=timeout,
                                    api_key=api_key)
    

    elif(api=="mistral"):

        return MistralAIMultiModal(model=model, 
                                    max_tokens=max_new_tokens, 
                                    # context_window = context_window,
                                    # image_detail= image_detail,
                                    max_retries=max_retries,
                                    timeout=timeout,
                                    api_key=api_key,
                                    output_parser=_safe_parse)


    elif(api=="gemini"):

        return GeminiMultiModal(model=model, 
                                max_new_tokens=max_new_tokens, 
                                context_window = context_window,
                                image_detail= image_detail,
                                max_retries=max_retries,
                                timeout=timeout,
                                api_key=api_key)

    elif(api=="ollama"):

        return OllamaMultiModal(model=model, 
                                max_new_tokens=max_new_tokens, 
                                context_window = context_window,
                                image_detail= image_detail,
                                max_retries=max_retries,
                                timeout=timeout)

    else:

        raise ValueError(f"The {model} initialization is not implemented yet. The available multimodalAI are : \
                         'openai', 'mistral'")