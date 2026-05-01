# user_preference_interface

This repository contains the developed interface adapted for the experiments conducted.

```
├── experiment_data                         --> data collected during the preliminary experiments
├── test_dataset                            --> test dataset used for preliminary experiments
├── exp_1_preference_interface.py           --> Preference translator experiment test    
├── exp_preference_translator_init.py       --> Ruleset creation for preference translator experiment
└──preference_interface.py                  --> Example usage of the preference interface
```

## Installation
This package can be installed by the following command
```
pip install -r requirements.txt # Not needed if any one of the requirements.txt file in context predictor, preference translator or rule updater is executed
pip install -e .
```

## Usage
An example usage of the developed interface is provided here

```
from user_preference_interface.preference_interface import UserPreferenceInterface
pref_interface = UserPreferenceInterface(log_file="log_file.csv", # change
                                        discrete_preference_vector=False) # True to predict discrete preference
print("Preference interface initiated")

## Rule updating

scene_info = pref_interface.get_scene_information("path to image")
pref_interface.update_rule_set(scene_info, "Do not go near the table")

## Prediction of pref vector

pref_interface.run("path to image")
```