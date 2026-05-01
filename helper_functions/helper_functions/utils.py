'''
This file contains the common helper functions. Following are the available helper functions,

1. read_yaml(file_path)
2. write_yaml(data, file_path)
3. read_txt(file_path)
4. read_excel_to_json(file_path)

'''



import yaml
import pandas as pd
import json
import csv
import copy
import os
import numpy as np
from collections import defaultdict
import random
import datetime
### Common helper function ####

def read_yaml(file_path):

    with open(file_path, 'r') as file:
        data = yaml.safe_load(file) 

    return data

def write_yaml(data, file_path):

    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


def read_txt(file_path):

    with open(file_path, 'r') as file:
        data = file.read()

    return data

def add_path_prefix_to_args(prefix, *args):
    
    updated_args = [os.path.join(prefix, str(arg)) for arg in args]
    
    return updated_args

def save_dict_to_csv(file_path, data_dict):
    keys = list(data_dict.keys())
    values = list(data_dict.values())

    if not os.path.isfile(file_path):
        # File doesn't exist: Write keys as first column and values as second
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Questions'] + ['Image_idx_1'])
            for key, value in zip(keys, values):
                writer.writerow([key, value])
    else:
        # File exists: Read current data
        with open(file_path, mode='r', newline='') as file:
            reader = list(csv.reader(file))
        
        # Add new header for the next column
        reader[0].append(f'Image_idx_{len(reader[0])}')  # Label as value2, value3, etc.

        # Append values to corresponding rows
        for i, row in enumerate(reader[1:]):
            key = row[0]
            row.append(str(data_dict.get(key, '')))  # Fill with empty if key missing

        # Write back the updated data
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(reader)

##### Rule updater helper functions #####

def read_csv_to_json(file_path):

    csv_data = pd.read_csv(file_path, encoding="utf-8")
    json_data = json.loads(csv_data.to_json(orient='records'))

    return json_data


def json_to_str(json_data):
    data = ""

    for i in json_data:

        data += json.dumps(i)+"\n"

    return data

def update_baseline_objectives(file_path, baseline_objectives):

    rules_dict = {"Baseline_objectives":[]}

    for rule in baseline_objectives:
        rules_dict["Baseline_objectives"].append(rule)

    baseline_objectives = yaml.dump(rules_dict, default_flow_style=False)

    write_yaml(rules_dict, file_path)
    

    return baseline_objectives

def delete_rules_by_id(rule_set_csv_data, rule_ids_to_delete):
    count = 0
    for id in rule_ids_to_delete:
        id = id-count
        rule_set_csv_data.pop(id)
        count+=1

    return rule_set_csv_data

def modify_rules_by_id(rule_set_csv_data, rule_ids_to_modify, modified_rules):


    for i in range(len(rule_set_csv_data)):

        if rule_set_csv_data[i]["rule_id"] in rule_ids_to_modify:

            idx = rule_ids_to_modify.index(rule_set_csv_data[i]['rule_id'])

            rule_set_csv_data[i]["human_feedback"] = modified_rules[idx].human_feedback
            rule_set_csv_data[i]["date_and_time"] = modified_rules[idx].date_and_time
            rule_set_csv_data[i]["lighting_condition"] = modified_rules[idx].lighting_condition
            rule_set_csv_data[i]["room_type"] = modified_rules[idx].room_type
            rule_set_csv_data[i]["human_presence"] = modified_rules[idx].human_presence
            rule_set_csv_data[i]["objects_in_scene"] = modified_rules[idx].objects_in_scene
            rule_set_csv_data[i]["rule"] = modified_rules[idx].rule
            rule_set_csv_data[i]["reason"]=modified_rules[idx].reason

    return rule_set_csv_data


def update_rule_ids(rule_set_csv_data):

    for i in range(len(rule_set_csv_data)):

        rule_set_csv_data[i]["rule_id"] = i

    return rule_set_csv_data

def update_context_based_rules_csv(file_path, rule_set_instance, participant_id, model):

    rule_set_csv_data = read_csv_to_json(file_path)

    ruleset_vars = vars(rule_set_instance)

    if(len(ruleset_vars['rule_ids_to_delete'])>0):

        rule_set_csv_data = delete_rules_by_id(rule_set_csv_data, ruleset_vars['rule_ids_to_delete'])


    if(len(ruleset_vars["rule_ids_to_modify"])>0):

        rule_set_csv_data = modify_rules_by_id(rule_set_csv_data, ruleset_vars['rule_ids_to_modify'], ruleset_vars['modified_rules'])


    # print("rule set vars : ", ruleset_vars)
    # json_data =[]
    rule_dict = {"timestamp":datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
                 "participant_id":participant_id,
                 "model":model,
                 "rule_id":"",
                 "human_feedback":"",
                 'date_and_time':"",
                 'lighting_condition':"",
                 'room_type':"",
                 'human_presence':"",
                 'objects_in_scene':"",
                 'rule':"",
                 'reason':"",
                 'explanation':""
                 }

    for i in range(0, len(ruleset_vars['rules_to_add'])):
        
        rule_dict['rule_id'] = ""
        rule_dict['human_feedback'] = ruleset_vars['rules_to_add'][i].human_feedback #   ruleset_vars['human_feedback'][i]
        rule_dict['date_and_time'] = ruleset_vars['rules_to_add'][i].date_and_time # ruleset_vars['date_and_time'][i]
        rule_dict['lighting_condition'] = ruleset_vars['rules_to_add'][i].lighting_condition #ruleset_vars['lighting_condition'][i]
        rule_dict['room_type'] = ruleset_vars['rules_to_add'][i].room_type  #ruleset_vars['room_type'][i]
        rule_dict['human_presence'] = ruleset_vars['rules_to_add'][i].human_presence #ruleset_vars['human_presence'][i]
        rule_dict['objects_in_scene'] = ruleset_vars['rules_to_add'][i].objects_in_scene #ruleset_vars['objects_in_scene'][i]
        rule_dict['rule'] = ruleset_vars['rules_to_add'][i].rule #ruleset_vars['rule'][i]
        rule_dict["reason"]=ruleset_vars['rules_to_add'][i].reason
        rule_dict["explanation"]=ruleset_vars["explanation"]
        rule_set_csv_data.append(copy.deepcopy(rule_dict))

    rule_set_csv_data = update_rule_ids(rule_set_csv_data)
    # print("Json data before writing : ", json_data)

    df = pd.DataFrame(rule_set_csv_data)

    # print("data frame for wrting : ", df)
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        # Create a CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=rule_set_csv_data[0].keys())
        
        # Write the header row (column names)
        writer.writeheader()
        
        # Write the data rows
        writer.writerows(rule_set_csv_data)


def update_log_data_csv(file_path, log_info):

    json_data =[log_info]
    df = pd.DataFrame(json_data)
    
    # print("data frame for wrting : ", df)
    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        # Create a CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=json_data[0].keys())
        
        writer.writerows(json_data)

def update_csv_data(file_path, data):

    json_data =[data]
    df = pd.DataFrame(json_data)
    
    # print("data frame for wrting : ", df)
    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        # Create a CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=json_data[0].keys())

        # Write the data rows
        writer.writerows(json_data)


def create_csv(file_path, headers):


# Create a new CSV file and write the headers
    with open(file_path, mode="w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        writer.writeheader()  # Write the header row


def extract_room_type_from_file_path(file_path):
    
    filename = os.path.basename(file_path)
    name_parts = os.path.splitext(filename)[0].split('_')

    room_type = '_'.join(name_parts[:-1])

    return room_type


def categorize_image_paths(image_folder):
    

    # Dictionary to hold image paths grouped by room type
    image_dict = defaultdict(list)

    # Loop through all files in the folder
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):  # add other image formats if needed
            # Extract the room type from filename (e.g., 'bedroom' from 'bedroom_1.jpg')
            room_type = filename.split('_')[0]
            # Full path to the image
            full_path = os.path.join(image_folder, filename)
            # Add to the dictionary
            image_dict[room_type].append(full_path)

    # Convert defaultdict to regular dict (optional)
    image_dict = dict(image_dict)

    return image_dict


def select_equal_images(image_dict, num_per_room):
    """
    Selects the same number of images from each room type.

    Parameters:
        image_dict (dict): room_type -> list of image paths
        num_per_room (int): number of images to select per room

    Returns:
        dict: room_type -> selected image paths
    """
    selected_images = {}
    
    for room, images in image_dict.items():
        if len(images) < num_per_room:
            print(f"⚠️ Not enough images in {room}. Only {len(images)} available.")
        selected_images[room] = random.sample(images, min(num_per_room, len(images)))
    
    return selected_images


def split_images_equally(image_dict, num_per_room):
    """
    Selects an even number of images per room, splits into two groups.

    Returns:
        group1, group2: Lists of image paths
    """
    group1, group2 = [], []

    for room, images in image_dict.items():
        if len(images) < num_per_room:
            print(f"⚠️ Not enough images in '{room}'. Only {len(images)} available.")
            selected = images  # take all available
        else:
            selected = random.sample(images, num_per_room)
        
        half = len(selected) // 2
        group1.extend(selected[:half])
        group2.extend(selected[half:])
    
    return group1, group2