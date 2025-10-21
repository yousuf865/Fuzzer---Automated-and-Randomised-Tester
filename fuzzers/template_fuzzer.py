class TemplateFuzzer:
    def __init__(self):
        self.max_val = 257

    def take_input(self, file_path: str) -> dict:
        with open(file_path, newline='') as sample_file:
            reader = "WAY TO READ IN FILE TYPE! Example for csv: csv.reader(sample_file)"
            field_1 = next(reader)
            field_2 = next(reader)
            field_3 = next(reader)
        
        normal_input_dict = {
            "field_1": field_1,
            "field_2": field_2,
            "field_3": field_3
        }
        return normal_input_dict
    
    def pattern(self, 
        field_1,
        field_2,
        field_3,
    ) -> str:
        input_pattern ='''
        Logic to map the pattern of the file type
        This allows us to basically generate an input pattern for the file type
        Implementations may vary a lot depending on the file type
        '''
        return input_pattern

    # This basically allows us to pick whether we want to mutate a specific field in the csv pattern
    def mutation_parameters(self, 
        # These are the fields that we can mutate
        field_1: bool, 
        field_2: bool, 
        field_3: bool, 
        normal_values: dict,
    ) -> list:
        # print("All inputs:\n",mutate_header, mutate_num_rows, mutate_num_cols, mutate_value_type, mutate_cell_val_len, normal_values, value_type)
        if field_1:
            print("Logic to mutate field_1!")
        else:
            field_1 = normal_values['field_1']

        if field_2:
            print("Logic to mutate field_2!")
        else:
            field_2 = normal_values['field_2']

        if field_3:
            print("Logic to mutate field_3!")
        else:
            field_3 = normal_values['field_3']
        
        mutation_dict = {
            "field_1": field_1,
            "field_2": field_2,
            "field_3": field_3
        }
        return self.pattern(field_1, field_2, field_3), mutation_dict
