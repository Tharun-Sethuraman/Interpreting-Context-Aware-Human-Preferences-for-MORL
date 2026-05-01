from helper_functions.utils import read_yaml, read_csv_to_json, update_baseline_objectives, json_to_str, update_context_based_rules_csv
from llama_index.core.bridge.pydantic import BaseModel, Field

# from llama_index.core.output_parsers.langchain import LangchainOutputParser

from llama_index.core.output_parsers.base import OutputParserException


from llama_index.core.program import LLMTextCompletionProgram

# from llama_index.llms.openai import OpenAI
# from llama_index.agent.openai import OpenAIAgent
from preference_translator.llm_init import init_llm_agent

from typing import List
import yaml
import pandas as pd
import datetime
import os


class RuleWithContext(BaseModel):

    human_feedback: str = Field(description="The human feedback used in the prompt. \
                                      Dont change anything to human feedback given. If the \
                                      human feeback contains multiple rules, split it into list of rules")

    date_and_time: str = Field(description="For new user feedback include 'time'. Keep the date and time for previous rules same")

    lighting_condition: str = Field(description="Extract lighting condition from contextual information \
                                          or extract it from human feedback. Only output following lighting conditions \
                                          Bright, Gentle, Low")

    room_type: str = Field(description="Room type identified from contextual information.\
                                  If a human mentions rule is for different room type, then include that room type")
    
    human_presence: str = Field(description="Extract human presence from the contextual \
                                       information ('True'/'False'/'Not specified'). If the user give rule in different \
                                        context, then extract human presence from the human feedback")
    
    objects_in_scene: str = Field(description="Objects from the extracted contextual information.\
                                               If the human feedback points to different context, then include \
                                              objects mentioned in feedback. If no objects mentioned, then return \
                                              'Not Specified' ")
    
    rule: str = Field(description="Convert human feedback into structured well formatted rule")

    reason: str = Field(description="Give a 2-3 line explanation how the user preference is reflection in the generated rule. Explain it in layman terms")

class RuleSetFormatWithContext(BaseModel):

    baseline_objectives: List[str] = Field(description="The baseline objectives that the robot should follow")

    rule_ids_to_delete: List[int] = Field(description="The list of rule ids to remove from the list of rules")

    rule_ids_to_modify: List[int] = Field(description="The list of rule ids to modify from the list of rules")

    modified_rules: List[RuleWithContext] = Field(description="The list of modified rules to add to the ruleset")

    rules_to_add: List[RuleWithContext] = Field(description="The list of new rules to add to the ruleset")

    explanation: str = Field(description="Give explanation of how the rules are created from given human feedback")

# class RulesSetFormatWithContext(BaseModel):

#     baseline_objectives: List[str] = Field(description="The baseline objectives that the robot should follow")

#     human_feedback: List[str] = Field(description="The human feedback used in the prompt. \
#                                       Dont change anything to human feedback given. If the \
#                                       human feeback contains multiple rules, split it into list of rules")
    
#     date_and_time: List[str] = Field(description="For new user feedback include 'time'. Keep the date and time for previous rules same")

#     lighting_condition: List[str] = Field(description="Extract lighting condition from contextual information \
#                                           or extract it from human feedback. Only output following lighting conditions \
#                                           Bright, Gentle, Low")

#     room_type: List[str] = Field(description="Room type identified from contextual information.\
#                                   If a human mentions rule is for different room type, then include that room type")
    
#     human_presence: List[bool] = Field(description="Extract human presence from the contextual \
#                                        information (True/False). If the user give rule in different \
#                                         context, then extract human presence from the human feedback")
    
#     objects_in_scene: List[str] = Field(description="Objects from the extracted contextual information.\
#                                                If the human feedback points to different context, then include \
#                                               objects mentioned in feedback. If no objects mentioned, then return \
#                                               'Not Specified' ")
    
#     rule: List[str] = Field(description="Convert human feedback into structured well formatted rule")

#     reason: str = Field(description="Explain why you have removed or added particular rule")


USER_FEEDBACK_PROMPT = ("The extracted contextual information are {context}. The existing rules are {rules} \n and the Feed back from user is : {user_input}. Compile the rules")

class RuleUpdater:

    def __init__(self, 
                 cfg_file_path="cfg/llm_params.yaml", 
                 system_prompt_path="system_prompt/system_prompt.txt", 
                 baseline_rules_file_path="rule_set/baseline_objectives.yaml", 
                 context_rules_file_path="rule_set/context_based_rules.csv",
                 participant_id=""):
        
        self.participant_id = participant_id
        # Get directory of this script
        self.current_dir_prefix = os.path.dirname(os.path.realpath(__file__))
        
        # Add prefix path for configurations
        # In case of different file, provide absolute path. Else default path will be taken
        self.baseline_rules_file_path = baseline_rules_file_path if os.path.isabs(baseline_rules_file_path) else os.path.join(self.current_dir_prefix, baseline_rules_file_path)
        self.context_rules_file_path = context_rules_file_path if os.path.isabs(context_rules_file_path) else os.path.join(self.current_dir_prefix, context_rules_file_path)
        self.cfg_file_path = cfg_file_path if os.path.isabs(cfg_file_path) else os.path.join(self.current_dir_prefix, cfg_file_path)
        self.system_prompt_path = system_prompt_path if os.path.isabs(system_prompt_path) else os.path.join(self.current_dir_prefix, system_prompt_path)

        print("context based rules path : ", self.context_rules_file_path)
        # Read LLM cfg, Rules (baseline and context based rules) and system prompt
        self.rule_updater_llm_cfg = read_yaml(self.cfg_file_path)
        self.rules = self.read_rules()
        with open(self.system_prompt_path, 'r') as file:
            SYSTEM_PROMPT = file.read()

        # Initialize LLM agent
        self.rule_updater_llm = init_llm_agent(api=self.rule_updater_llm_cfg["api"],
                                               model=self.rule_updater_llm_cfg["model"], 
                                               max_tokens=self.rule_updater_llm_cfg["max_tokens"], 
                                               max_retries=self.rule_updater_llm_cfg["max_retries"],
                                               timeout=self.rule_updater_llm_cfg["timeout"],
                                               api_key=self.rule_updater_llm_cfg["api_key"],
                                               system_prompt = SYSTEM_PROMPT )
        
        
        self.rule_updater = LLMTextCompletionProgram.from_defaults(
                                    # output_parser=LangchainOutputParser, 
                                    output_cls=RuleSetFormatWithContext,
                                    prompt_template_str = USER_FEEDBACK_PROMPT, 
                                    llm=self.rule_updater_llm
                                    )
        

        self.connection_test_run()
        
    def update_rules(self, context, user_feedback):
        self.rules = self.read_rules()
        rules = self.rule_updater(context=context, rules=self.rules, user_input=user_feedback)

        rules = self.update_time_for_new_rules(rules)
        print(rules)
        update_baseline_objectives(self.baseline_rules_file_path, vars(rules)['baseline_objectives'])
        update_context_based_rules_csv(self.context_rules_file_path, rules, participant_id=self.participant_id, model=self.get_model_name())
        return rules
    

    def update_single_rule(self, context, user_feedback, rules_file_path):
        # print(self.read_rules())
        print("provided user feedback", user_feedback)
        rules = self.rule_updater(context=context, rules="", user_input=user_feedback)
        rules = self.update_time_for_new_rules(rules)
        print(rules)
        update_context_based_rules_csv(rules_file_path, rules, participant_id=self.participant_id, model=self.get_model_name())

        return rules
    
    def connection_test_run(self,):
        print("--------------------------")
        print("---Connection test--------")
        print("--------------------------")

        self.rule_updater(context="", rules="", user_feedback="Robot should go slow")


    def read_rules(self,):

        baseline_objectives = yaml.dump( read_yaml(self.baseline_rules_file_path) , default_flow_style=False)  # read rules from an yaml file and convert it into string

        context_based_rules = read_csv_to_json(self.context_rules_file_path) # read rules from an excel file and return as json string

        context_based_rules = json_to_str(context_based_rules)

        rules = baseline_objectives + "\nContext based rules:\n" + context_based_rules

        return rules
    
    def update_time_for_new_rules(self, rules):

        time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

        if len(rules.modified_rules)>0:

            for i in range(0, len(rules.modified_rules)):

                if rules.modified_rules[i].date_and_time == "time":

                    rules.modified_rules[i].date_and_time =time

        if len(rules.rules_to_add)>0:

            for i in range(0, len(rules.rules_to_add)):

                if rules.rules_to_add[i].date_and_time == "time":

                    rules.rules_to_add[i].date_and_time=time

        return rules

    def get_model_name(self):

        return self.rule_updater_llm_cfg["model"]