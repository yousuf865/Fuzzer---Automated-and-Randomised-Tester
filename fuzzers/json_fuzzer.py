

import random
import string
import json
class JSONFuzzer:
    def __init__(self):
        self.max_val = 257
        self.min_val = 0

    def get_max_val(self):
        return self.max_val

    def set_max_val(self, max_val: int):
        self.max_val = max_val
    
    def get_min_val(self):
        return self.min_val
    
    def set_min_val(self, min_val: int):
        self.min_val = min_val

    def detect_value_type(self, value):
        try:
            int(value)
            return 'int'
        except ValueError:
            try:
                float(value)
                return 'float'
            except ValueError:
                if value.startswith('0x') and all(c in string.hexdigits for c in value[2:]):
                    return 'hex'
                elif all(c in '01' for c in value):
                    return 'bin'
                else:
                    return 'str'
        
    def take_input(self,
                   file_path: str) -> dict:
        with open(file_path, 'r') as file:
            content = file.read()
            content=json.loads(content)
            normal_input_dict={
                "base":content
            }
            return normal_input_dict
        
    def pattern(self, base:dict)->str:
        # If the base is a dictionary (object), we mutate each key-value pair
        if isinstance(base, dict):
            payload = {}
            for key, value in base.items():
                payload[key]=value
            return payload

    def mutation_parameters(self,empty_or_nonjson:bool, large_num: bool,
                            large_input:bool, random_structure: bool,  invalid_chars: bool,
                            fstring:bool,large_integer_list:bool,
                            all_blank:bool,all_null:bool,wrong_input:bool,normal_values: dict) -> list:

        base = normal_values['base']
        payload = self.pattern(base)
        mutation_type=[]
        # Randomly determine the base length of the input
        if empty_or_nonjson:
            choice = random.choice(["empty_payload","non_json"])
            if choice == "empty_payload":
                mutation_type.clear()
                mutation_type.append("Empty Payload")
                payload= {}
                
                #return json.dumps(payload), mutation_type
            
            elif choice== "non_json":
                random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0,20000)))  # Random string length between 5 and 10
                payload = f"{random_str}"
                mutation_type.clear()
                mutation_type.append("Non-Json Payload")
                

                #return json.dumps(payload),mutation_type 
        else:
            # This just means the structure is normal
            pass

        if large_num:
            if isinstance(payload,dict):
                for key,value in payload.items():
                    if isinstance(value,int):
                        payload[key]=random.randint(100, self.max_val)
                mutation_type.append("Large Number")

        if large_input:
            if isinstance(payload,dict):
                for key,value in payload.items():
                    if isinstance(value,str):
                        payload[key] = ''.join(random.choices(string.ascii_lowercase, k=random.randint(100, self.max_val)))
                mutation_type.append("Large Input")

        if random_structure: #cause stack smashing in json2
            if isinstance(payload,dict):
                # Create a new random key and value
                for i in range(random.randint(10, self.max_val)):
                    additional_key = f'key_{i}' 
                    additional_value = ''.join(random.choices(string.ascii_lowercase, k=random.randint(10,self.max_val))) 
                    payload[additional_key] = additional_value  
                mutation_type.append("Random Structure")

        # Handle different types of mutations
        if invalid_chars:
            if isinstance(payload,dict):
                # Randomly select an invalid character injection strategy
                invalid_character = random.choice(['\x00', '\x1F', '\x7F'])  # Example invalid characters

                for key in payload:
                    if isinstance(payload[key], str):
                        payload[key] += invalid_character  
                mutation_type.append("Invalid Character")
            
        if fstring:
            if isinstance(payload,dict):
                for key in payload:
                    if isinstance(payload[key], str):
                        payload[key] = ''.join(random.choices(["%s", "%x", "%n ","%d","%p","%c"], k=20))
                mutation_type.append("fstring")

        if large_integer_list:
            if isinstance(payload,dict):
                for key,value in payload.items():
                    if isinstance(value,list):
                        for i in range (len(value)):
                            if isinstance(value[i],int):
                                value[i]=random.randint(100, self.max_val)
                mutation_type.append("Large Integer List")

        if all_blank:
            if isinstance(payload,dict):
                for key,value in payload.items():
                    if isinstance(value,str):
                        payload[key]=''
                    if isinstance(value,int):
                        payload[key]=0
                    if isinstance(value,list):
                        for i in range (len(value)):
                            if isinstance(value[i],int):
                                value[i]=0
                            if isinstance(value[i],str):
                                value[i]=''
            
        if all_null:
             if isinstance(payload,dict):
                for key,value in payload.items():
                    payload[key] = None

        if wrong_input:      
            if isinstance(payload,dict):
                for key,value in payload.items():
                    if isinstance(value,int):
                        payload[key]="switch to string"
                    if isinstance(value,str):
                            payload[key]=123456789
        
        mutation_dict = {
            "empty_or_nonjson": empty_or_nonjson,
            "large_num": large_num,
            "large_input": large_input,
            "random_structure": random_structure,
            "invalid_chars": invalid_chars,
            "fstring": fstring,
            "large_integer_list": large_integer_list,
            "all_blank":all_blank,
            "all_null":all_null,
            "wrong_input":wrong_input
        }



        return json.dumps(payload), mutation_dict
