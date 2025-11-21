import random, string
class PlainTextFuzzer:
    def __init__(self):
        self.max_val = 2147483648
        self.min_val = -2147483648
    
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
        with open(file_path, newline='') as txtfile:
            content = txtfile.readlines()
            header = content[0].strip('\n')

            num_lines = 0
            value_types = set()

            max_input_len = 0
            for line in content:
                strip_line = line.strip('\n')
                num_lines += 1
                input_val_len = len(strip_line)
                if input_val_len > max_input_len:
                    max_input_len = input_val_len
                value_types.add(self.detect_value_type(line))

            input_len = max_input_len
            if len(value_types) > 1:
                value_type = 'mix'
            else:
                value_type = next(iter(value_types)) if value_types else 'unknown'

        normal_input_dict = {
            "header": header,
            "num_lines" : num_lines,
            "value_type": value_type,
            "input_len": input_len
        }
        return normal_input_dict


    def pattern(self,
        header: str,
        num_lines: int,
        value_type: str,
        input_len: int
    ) -> str: 
        header = header
        input_pattern = ""
        for _ in range(num_lines):
            if value_type == "int":
                row = [str(random.randint(0, self.max_val))]
            elif value_type == "float":
                row = [str(random.uniform(0, self.max_val))]
            elif value_type == "hex":
                row = [hex(random.randint(0, self.max_val))]
            elif value_type == "bin":
                row = [bin(random.randint(0, self.max_val))]
            elif value_type == "mix":
                row = [random.choice([str(random.randint(0, self.max_val)), str(random.uniform(0, self.max_val)), hex(random.randint(0, self.max_val)), bin(random.randint(0, self.max_val)), ''.join(random.choices(string.ascii_lowercase, k=input_len))])]
            else:
                row = [''.join(random.choices(string.ascii_lowercase, k=input_len))]
            input_pattern += ",".join(row) + "\n"
        return input_pattern
    
    def mutation_parameters(self,
        mutate_header: bool,
        mutate_num_lines: bool,
        mutate_value_type: bool,
        mutate_input_len: bool,
        normal_values: dict,
        value_type: str = random.choice(["str", "int", "float", "hex", "bin", "mix"]),
    ) -> list:

        header = normal_values['header']

        if mutate_num_lines:
            num_lines = random.randint(1, self.max_val)
        else:
            num_lines = normal_values['num_lines']

        if mutate_value_type:
            value_type = value_type
        else:
            value_type = normal_values['value_type']

        if mutate_input_len:
            input_len = random.randint(1, self.max_val)
        else: 
            input_len = normal_values['input_len']

        mutation_dict = {
            "header": header,
            "num_lines": num_lines,
            "value_type": value_type,
            "input_len": input_len
        }

        return self.pattern(header, num_lines, value_type, input_len), mutation_dict