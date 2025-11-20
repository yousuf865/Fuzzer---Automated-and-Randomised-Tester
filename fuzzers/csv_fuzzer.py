import csv
import random
import string
class CSVFuzzer:
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
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            # Read the header
            header = next(reader)
            num_cols = len(header)
            
            # Initialize counters and storage
            num_rows = 0
            cell_val_len = 0
            value_types = set()
            
            # Process each row
            max_cell_len = 0
            for row in reader:
                num_rows += 1
                for cell in row:
                    cell_len = len(cell)
                    if cell_len > max_cell_len:
                        max_cell_len = cell_len
                    value_types.add(self.detect_value_type(cell))
            cell_val_len = max_cell_len
            # Determine the overall value type
            if len(value_types) > 1:
                value_type = 'mix'
            else:
                value_type = next(iter(value_types)) if value_types else 'unknown'

        normal_input_dict = {
            "header": header, 
            "num_rows": num_rows, 
            "num_cols": num_cols, 
            "value_type": value_type, 
            "cell_val_len": cell_val_len
        }
        return normal_input_dict
        # what breaks it:
        # ,\n
        # b'',b''
    
    def pattern(self, 
        header: list, 
        num_rows: int, 
        num_cols: int, 
        value_type: str, 
        cell_val_len: int
    ) -> str:
        headers = header
        input_pattern = ""
        for _ in range(num_rows):
            csv_delim = ","
            # self.max_val = 10**cell_val_len - 1
            # k is the number of characters in the string
            if value_type == "int":
                row = [str(random.randint(0, self.max_val)) for _ in range(0, num_cols)]
            elif value_type == "float":
                row = [str(random.uniform(0, self.max_val)) for _ in range(0, num_cols)]
            elif value_type == "hex":
                row = [hex(random.randint(0, self.max_val)) for _ in range(0, num_cols)]
            elif value_type == "bin":
                row = [bin(random.randint(0, self.max_val)) for _ in range(0, num_cols)]
            elif value_type == "mix":
                row = [random.choice([str(random.randint(0, self.max_val)), str(random.uniform(0, self.max_val)), hex(random.randint(0, self.max_val)), bin(random.randint(0, self.max_val)), ''.join(random.choices(string.ascii_lowercase, k=cell_val_len))]) for _ in range(0, num_cols)]
            elif value_type == "neg":
                row = [str(random.randint(-1*self.max_val, self.max_val)) for _ in range(0, num_cols)]
            elif value_type == "delim":
                row = [''.join(random.choices(string.ascii_lowercase, k=cell_val_len)) for _ in range(0, num_cols)]
                delim_list = [' ', '.', ',', '\t', '\n', '|', '/', '\\', ':', ';']
                csv_delim = f"{random.choice(delim_list)}"
            elif value_type == "format":
                # Fill each cell with a random format specifier
                format_specifiers = ['%s', '%d', '%f', '%x', '%o', '%e', '%g', '{:s}', '{:d}', '{:f}', '{:x}', '{:o}', '{:e}', '{:g}']
                row = [",".join(random.sample(format_specifiers, k=random.randint(1, len(format_specifiers)))) for _ in range(0, num_cols)]
            else:
                row = [''.join(random.choices(string.ascii_lowercase, k=cell_val_len)) for _ in range(0, num_cols)]
            if _ == 0:
                input_pattern += ",".join(headers) + "\n"
            final_input_pattern = csv_delim.join(row) + "\n"
            input_pattern += final_input_pattern
        return input_pattern

    # This basically allows us to pick whether we want to mutate a specific field in the csv pattern
    def mutation_parameters(self, 
        mutate_header: bool, 
        mutate_num_rows: bool, 
        mutate_num_cols: bool, 
        mutate_value_type: bool, 
        mutate_cell_val_len: bool, 
        normal_values: dict,
        value_type: str = "default",
    ) -> list:
        # print("All inputs:\n",mutate_header, mutate_num_rows, mutate_num_cols, mutate_value_type, mutate_cell_val_len, normal_values, value_type)
        if value_type == "default":
            value_type = random.choice(["str", "int", "float", "hex", "bin", "mix", "neg", "delim", "format"])
        if mutate_header:
            header = [
                ''.join(random.choices(string.ascii_lowercase, k=random.randint(0, self.max_val)))
                for _ in range(0, self.max_val)
            ]
        # Create logic that allows a field to go unused
        else:
            header = normal_values['header']

        if mutate_num_rows:
            num_rows = random.randint(1, self.max_val)
        else:
            num_rows = normal_values['num_rows']
        
        if mutate_num_cols:
            num_cols = random.randint(1, self.max_val)
        else:
            num_cols = normal_values['num_cols']
        
        if mutate_value_type:
            value_type = value_type
        else:
            value_type = normal_values['value_type']
        
        if mutate_cell_val_len:
            cell_val_len = random.randint(1, self.max_val)
        else: 
            cell_val_len = normal_values['cell_val_len']
        
        mutation_dict = {
            "header": header,
            "num_rows": num_rows,
            "num_cols": num_cols,
            "value_type": value_type,
            "cell_val_len": cell_val_len
        }
        return self.pattern(header, num_rows, num_cols, value_type, cell_val_len), mutation_dict
