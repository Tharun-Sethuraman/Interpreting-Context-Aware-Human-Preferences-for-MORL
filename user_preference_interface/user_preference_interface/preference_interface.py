from api_usage_monitor.api_usage_monitor import ApiUsageMonitor
from rule_updater.rule_updater import RuleUpdater
from preference_translator.preference_translator import LLMPreferenceTranslator
from llm_context_predictor.context_predictor import VLMContextPredictor
from helper_functions.utils import update_log_data_csv, read_yaml, read_csv_to_json
import time
import os
from tqdm import tqdm

class UserPreferenceInterface:

    def __init__(self, log_file="",
                 discrete_preference_vector=False):
        
        self.context_predictor = VLMContextPredictor()
        self.rule_updater = RuleUpdater()
        self.preference_translator = LLMPreferenceTranslator(discrete_preference_vector=discrete_preference_vector)
        
        self.log_file =log_file

    def get_scene_information(self,image_path):
        scene_information = self.context_predictor.predict_context(image_path, "low")
        return str(scene_information)
    
    def update_rule_set(self, scene_information, predefined_rule):
        rules = self.rule_updater.update_rules(scene_information, predefined_rule)

    def run(self, 
            image_path, 
            user_feedback,
            act_room=None):

        inference_time =[0.0, 0.0, 0.0]

        start_time = time.time()
        scene_information = self.context_predictor.predict_context(image_path, "low")
        end_time = time.time()

        inference_time[0] = end_time-start_time

        print(f"CP inf_time {inference_time[0]}, Extracted info{scene_information}")

        # start_time = time.time()
        # rules = self.rule_updater.update_rules(scene_information, user_feedback)
        # end_time = time.time()

        inference_time[1] = end_time-start_time
        print(f"RU inf_time {inference_time[1]}, Rules updated")

        start_time = time.time()
        preference_vector, reason = self.preference_translator.predict_preference(str(scene_information))
        end_time = time.time()

        inference_time[2] = end_time-start_time

        print(f"PT inf_time {inference_time[2]}, The predicted pref vector :: {preference_vector}")
        self.log(image_path, act_room, scene_information, preference_vector, reason, inference_time)
        
    
    def log(self,image_path, act_room, scene_information, preference_vector, reason, inference_time):
        
        self.log_info = {"Cp_vlm":self.context_predictor.get_model_name(),
                         "Ru_llm":self.rule_updater.get_model_name(),
                         "Pt_llm":self.preference_translator.get_model_name(),
                         "Image_path":image_path,
                         "Act_room":act_room,
                         "Objects_detected":scene_information.objects,
                         "Human_presence":scene_information.is_human_present,
                         "Lighting":scene_information.lighting_condition,
                         "Pred_room":scene_information.room_type,
                         "Nav_Eff":preference_vector[0],
                         "Demo_eff":preference_vector[1],
                         "Dist_obstacle":preference_vector[2],
                         "Dist_human":preference_vector[3],
                         "Speed":preference_vector[4],
                         "Reason":reason, 
                         "Ct_inference_time":inference_time[0],
                         "Ru_Inference_time":inference_time[1],
                         "Pt_inference_time":inference_time[2]}
        
        update_log_data_csv(self.log_file, self.log_info)


# def main():

#     pref_interface = UserPreferenceInterface(log_file="",
#                                              discrete_preference_vector=True)
#     print("Preference interface initiated")

#     ## Rule updating

#     scene_info = pref_interface.get_scene_information("path to image")
#     pref_interface.update_rule_set(scene_info, "Do not go near the table")

#     ## Prediction of pref vector

#     pref_interface.run("path to image")

 

# if __name__ == "__main__":
#     main()
