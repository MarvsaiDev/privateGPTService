import prompt_res.prompts as prompts
import json
from prompt_res.prompt_dict import ExtractionPrompt
# Get the dictionary of variables defined in foo.py
module_variables = prompts.__dict__

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ExtractionPrompt):
            return obj.to_dict()  # Assuming you have a to_dict() method
        return super().default(obj)
# Print the variable names and their values
def get_format_definitions(keyvalue=None):
    list = []
    for var_name, var_value in module_variables.items():
        if isinstance(var_value, dict) and '__' not in var_name:
            value = var_value[keyvalue] if keyvalue else var_value
            print(f"{var_name}: {value}")
            list.append(value)
    return list

def create_extraction_prompt(keyvalue=None):
    list = {}
    for var_name, var_value in module_variables.items():
        if isinstance(var_value, dict) and '__' not in var_name:
            value = var_value[keyvalue] if keyvalue else var_value
            print(f"{var_name}: {value}")
            if 'default' in var_name:
                if 'default' in list:
                    list['default_plus'] = var_value
                else:
                    list['default'] = var_value
                    list['raw'] = var_value.copy()
            elif 'carah' in var_name:
                list['Cara'] = var_value
            else:
                list[var_name[0:3].upper()] = var_value
    return ExtractionPrompt(**list)
extraction_prompt = (create_extraction_prompt())
print(json.dumps(extraction_prompt, cls=CustomEncoder,sort_keys=True, indent=4))
