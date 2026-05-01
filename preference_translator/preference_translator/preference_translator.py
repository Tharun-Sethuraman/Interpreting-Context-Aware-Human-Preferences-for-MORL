from helper_functions.utils import read_yaml, read_csv_to_json, json_to_str
from llama_index.core.bridge.pydantic import BaseModel, Field

from llama_index.core.program import LLMTextCompletionProgram


from preference_translator.llm_init import init_llm_agent
from typing import List
import yaml
import os

PREF_PROMPT=("The rules are {rules}. The Scene information {scene_information}. Comments on previous usage {comments}")

class PreferenceVectorResponseFormat(BaseModel): # Format in which the gpt is should answer for continuous space numerical values
    navigational_efficiency: float = Field(description="The navigational effiency computed based on the given rules")
    demonstration_efficiency: float = Field(description="The demonstration_efficiency computed based on the given rules")
    obstacle_avoidance_efficiency: float = Field(description="The obstacle_avoidance_efficiency (distance to obstacles) computed based on the given rules")
    distance_keeping_to_human: float = Field(description="The distance_keeping_to_human computed based on the given rules")
    speed: float = Field(description="The speed of the robot computed based on the given rules")
    relevant_rules: List[str] = Field(description="List of relevant rules")
    reason: str = Field(description="Explanation of how relevant rules are extracted and used")


class PreferenceVectorTextResponseFormat(BaseModel): # Format in which the gpt is should answer for discrete textual output
    navigational_efficiency: str = Field(description="The navigational effiency computed based on the given rules")
    demonstration_efficiency: str = Field(description="The demonstration_efficiency computed based on the given rules")
    obstacle_avoidance_efficiency: str = Field(description="The obstacle_avoidance_efficiency (distance to obstacles) computed based on the given rules")
    distance_keeping_to_human: str = Field(description="The distance_keeping_to_human computed based on the given rules")
    speed: str = Field(description="The speed of the robot computed based on the given rules")
    relevant_rules: List[str] = Field(description="List of relevant rules")
    reason: str = Field(description="Explanation of how relevant rules are extracted and used")

class LLMPreferenceTranslator:

    def __init__(self, 
                 cfg_file_path="cfg/llm_params.yaml", 
                 system_prompt_path="system_prompt/system_prompt.txt", 
                 baseline_rules_file_path="../../rule_updater/rule_updater/rule_set/baseline_objectives.yaml",
                 context_rules_file_path="../../rule_updater/rule_updater/rule_set/context_based_rules.csv",
                 discrete_preference_vector=False,
                 participant_id=""):
        
        self.participant_id = participant_id
        # Get directory of this script
        self.current_dir_prefix = os.path.dirname(os.path.realpath(__file__))

        # Add prefix path for configurations
        # In case of different file, provide absolute path. Else default path will be taken
        self.baseline_rules_file_path = baseline_rules_file_path if os.path.isabs(baseline_rules_file_path) else os.path.join(self.current_dir_prefix, baseline_rules_file_path)
        self.context_rules_file_path = context_rules_file_path if os.path.isabs(context_rules_file_path) else os.path.join(self.current_dir_prefix, context_rules_file_path)
        self.cfg_file_path = cfg_file_path if os.path.isabs(cfg_file_path) else os.path.join(self.current_dir_prefix, cfg_file_path)
        
        if not discrete_preference_vector:
            self.system_prompt_path = system_prompt_path if os.path.isabs(system_prompt_path) else os.path.join(self.current_dir_prefix, system_prompt_path)
        else:
            self.system_prompt_path = system_prompt_path if os.path.isabs(system_prompt_path) else os.path.join(self.current_dir_prefix, "system_prompt/system_prompt_text_output.txt")

        # Flag - Genereate preference vector as discrete values or continuous space values
        self.discrete_preference_vector = discrete_preference_vector

        self.llm_cfg = read_yaml(self.cfg_file_path) # loading llm cfg from yaml file
        
        # Read system prompt
        with open(self.system_prompt_path, 'r') as file:
            SYSTEM_PROMPT = file.read()

        # Initialize LLM agent
        self.llm = init_llm_agent(api=self.llm_cfg["api"], 
                        model=self.llm_cfg["model"], 
                        max_tokens=self.llm_cfg["max_tokens"], 
                        max_retries=self.llm_cfg["max_retries"],
                        timeout=self.llm_cfg["timeout"],
                        api_key=self.llm_cfg["api_key"],
                        system_prompt = SYSTEM_PROMPT )
        
        # Changing Response format for discrete and continous values
        if not discrete_preference_vector: 

            self.pref_translator = LLMTextCompletionProgram.from_defaults(
                                        output_cls=PreferenceVectorResponseFormat,
                                        prompt_template_str = PREF_PROMPT, 
                                        llm=self.llm
                                        )
        else:

            self.pref_translator = LLMTextCompletionProgram.from_defaults(
                                        output_cls=PreferenceVectorTextResponseFormat,
                                        prompt_template_str = PREF_PROMPT, 
                                        llm=self.llm
                                        )
            
            self.preference_vector_map = { "extremely_low":0.0, 
                                          "very_low":0.1, 
                                          "low":0.2, 
                                          "moderately_low":0.3, 
                                          "medium_low":0.4, 
                                          "medium":0.5, 
                                          "moderately_high":0.6, 
                                          "high":0.7, 
                                          "quite_high":0.8, 
                                          "very_high":0.9, 
                                          "extremely_high":1.0 }


    def predict_preference(self, scene_information, comments=""):

        preference = self.pref_translator(rules = self.read_rules(), scene_information=scene_information, comments="")
        
        if self.discrete_preference_vector:
            print("Predicted prefeerence : ", preference)
            preference_vector = self.map_preference_vector_to_numeric(preference, scene_information)
        
        else:
            
            preference_vector = [preference.navigational_efficiency,
                                 preference.demonstration_efficiency,
                                 preference.obstacle_avoidance_efficiency,
                                 preference.distance_keeping_to_human,
                                 preference.speed]
            
        return preference_vector, preference.relevant_rules, preference.reason
    

    def read_rules(self,):

        baseline_objectives = yaml.dump( read_yaml(self.baseline_rules_file_path) , default_flow_style=False)  # read rules from an yaml file and convert it into string

        context_based_rules = read_csv_to_json(self.context_rules_file_path) # read rules from an excel file and return as json string

        context_based_rules = json_to_str(context_based_rules)

        rules = baseline_objectives + "\nContext based rules:\n" + context_based_rules

        return rules
    

    def map_preference_vector_to_numeric(self, preference, scene_information):
        preference_vector = [0.0, 0.0, 0.0, 0.0, 0.0]

        try:
        
            preference_vector[0] = self.preference_vector_map[preference.navigational_efficiency.lower()]
            preference_vector[1] = self.preference_vector_map[preference.demonstration_efficiency.lower()]
            preference_vector[2] = self.preference_vector_map[preference.obstacle_avoidance_efficiency.lower()]
            preference_vector[3] = self.preference_vector_map[preference.distance_keeping_to_human.lower()]
            preference_vector[4] = self.preference_vector_map[preference.speed.lower()]
        
        except:
            generated_values = [preference.navigational_efficiency.lower(), 
                                preference.demonstration_efficiency.lower(),
                                preference.obstacle_avoidance_efficiency.lower(),
                                preference.distance_keeping_to_human.lower(),
                                preference.speed.lower()]
            
            print("#"*20)
            print("Generate incorrect value for preference ", generated_values)
            print("#"*20)

            predefined_values = list(dict.keys(self.preference_vector_map))

            incorrect_values = []
            for preference_value in generated_values:

                if(preference_value not in predefined_values):
                    
                    incorrect_values.append(preference_value)

            
            comment = f"You have generated incorrect values such as {incorrect_values} in preference vector. So Respond with one of the predefined values : {predefined_values}."

            self.predict_preference(scene_information, comments=comment) 

        return preference_vector
    

    def get_model_name(self):

        return self.llm_cfg["model"]