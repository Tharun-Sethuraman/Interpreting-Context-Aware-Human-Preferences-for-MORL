# from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llm_context_predictor.mm_init import init_multimodal_llm
from llama_index.core.schema import ImageDocument

from llama_index.core.llms import ImageBlock

from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core.bridge.pydantic import BaseModel, Field

from api_usage_monitor.api_usage_monitor import ApiUsageMonitor
from helper_functions.utils import read_yaml

import yaml
import datetime
from typing import List, ClassVar
import os


class ResponseFormat(BaseModel): # Format in which the gpt is should answer
    objects: List[str] = Field(description="List of objects detected in the given scene")
    objects_distance: List[float] = Field(description="Distance to the list ofobjects detected in the scene")
    is_human_present: bool = Field(description="Output True if human present in the scene else false")
    lighting_condition: str = Field(description="Extract lighting conditions from the scene : \
                                    Bright or Gentle or Low ")
    room_type: str = Field(description="Identify the room type. The following are the room types available: \
                           Kitchen, Living room, Dinning room, Bed room")
    time: str = Field(description='A time')
    context: str = Field(description="Context of the environment in one or two sentences only")


class VLMContextPredictor:

    def __init__(self, 
                 cfg_file_path="cfg/vlm_params.yaml",
                 system_prompt_path="system_prompt/system_prompt.txt"):

        self.current_dir_prefix = os.path.dirname(os.path.realpath(__file__))
        
        self.cfg_file_path = cfg_file_path if os.path.isabs(cfg_file_path) else os.path.join(self.current_dir_prefix, cfg_file_path)
        self.vlm_cfg = read_yaml(self.cfg_file_path) # loading llm cfg from yaml file
        
        self.system_prompt_path = system_prompt_path if os.path.isabs(system_prompt_path) else os.path.join(self.current_dir_prefix, system_prompt_path)
        # Read system prompt
        with open(self.system_prompt_path, 'r') as file:
            SYSTEM_PROMPT = file.read()


        self.vlm = init_multimodal_llm(api=self.vlm_cfg["api"],
                                    model=self.vlm_cfg["model"], 
                                    max_new_tokens=self.vlm_cfg["max_tokens"], 
                                    context_window = self.vlm_cfg["context_window"],
                                    image_detail= self.vlm_cfg["image_detail"],
                                    max_retries=self.vlm_cfg["max_retries"],
                                    timeout=self.vlm_cfg["timeout"],
                                    api_key=self.vlm_cfg["api_key"])
        
        self.vlm_context_predictor = MultiModalLLMCompletionProgram.from_defaults(
                                        output_cls=ResponseFormat,
                                        prompt_template_str=SYSTEM_PROMPT,
                                        multi_modal_llm=self.vlm)

    def system_prompt(self, prompt):
        pass

    def predict_context(self, img_path, img_detail="low"):

        image_document = ImageBlock(path=img_path, detail=img_detail, image_mimetype="image/png")

        vlm_response = self.vlm_context_predictor(image_documents=[image_document])
        vlm_response.time= str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        return vlm_response


    def predict_context_from_imgbytes(self, img_bytes, img_detail="low"):

        image_document = ImageBlock(image=img_bytes, detail=img_detail, image_mimetype="image/png")

        vlm_response = self.vlm_context_predictor(image_documents=[image_document])
        vlm_response.time= str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        return vlm_response


    def get_model_name(self):

        return self.vlm_cfg["model"]