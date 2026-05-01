# preference_translator

This repository contains the implementation of the `Preference translator` of the proposed interface. The 
files in this repository are



```
├── cfg         
│   └── llm_params.yaml                ---> File consisting of parameters to initialize the LLM for preference translator
├── system_prompt
│   ├── prev_prompts                   ---> Folder containing system prompts experimented during the development phase
│   └── system_prompt.txt              ---> System prompt for predicting "Continuous preference vectors
├── llm_init.py                        ---> In this file initialisation of various models were done
├── preference_translator.py           ---> Preference translator developed for the proposed interface
```

## Installation
This package can be installed by the following command
```
pip install -r requirements.txt # Not needed if any one of the requirements.txt file in context predictor, preference translator or rule updater is executed
pip install -e .
```


## Configuration file

```
api: # The API to use eg: openai, mistral, gemini, ollama (for local llms)
model: #[str] The LLM model to use.
max_tokens: #[int] The maximum numbers of tokens to generate, ignoring the number of tokens in the prompt (default : 300)
context_window: #[int] The maximum number of context tokens for the model. (default :  DEFAULT_CONTEXT_WINDOW=3900)
max_retries: #[int] Maximum number of retries (default=3)
timeout: #[float] The timeout, in seconds, for API requests. (default=60.0s)
api_key: #[str] The API key. (can be set as env parameter)
# api_base: #[str] The base URL for API.
# api_version: #[str] The API version for API.
```

## Usage

```
preference_translator = LLMPreferenceTranslator(cfg_file_path="cfg/llm_params.yaml", # Path to the LLM configuration file
                                                baseline_rules_file_path="../../rule_updater/rule_updater/rule_set/baseline_objectives.yaml", # Path to the baseline objectives in YAMl format
                                                context_rules_file_path="../../rule_updater/rule_updater/rule_set/context_based_rules.csv", # Path to the context based ruleset in csv format
                                                discrete_preference_vector=False) # True - predict discrete preference vectors

preference_translator.predict_preference(self, scene_information) #scene_information - contextual information extracted by the VLM

```