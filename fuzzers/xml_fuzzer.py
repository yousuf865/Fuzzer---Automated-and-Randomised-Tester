import random
import string
from xml.etree.ElementTree import Element, tostring, fromstring, SubElement
import xml.etree.ElementTree as ET

class XMLFuzzer:
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

    def take_input(self, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            data = file.read()
            root = fromstring(data)
            return {"base": root}

    def pattern(self, base: Element) -> Element:
        cloned_root = Element(base.tag, base.attrib)
        for child in base:
            cloned_root.append(child)
        return cloned_root

    def mutation_parameters(self, empty_or_nonxml: bool, large_text: bool, random_structure: bool,
                            invalid_chars: bool, unclosed_tags: bool, large_attribute_list: bool,
                            all_blank: bool, wrong_input: bool, normal_values: dict) -> list:
        
        base = normal_values['base']
        payload = self.pattern(base)
        mutation_type = []

        # Empty or Non-XML Payload
        if empty_or_nonxml:
            choice = random.choice(["empty_payload", "non_xml"])
            if choice == "empty_payload":
                payload = Element("root")
                mutation_type.append("Empty Payload")
            elif choice == "non_xml":
                payload = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(0, 20000)))
                mutation_type.append("Non-XML Payload")
                return payload, mutation_type

        # Large Text Mutation
        if large_text:
            for elem in payload.iter():
                elem.text = ''.join(random.choices(string.ascii_letters, k=random.randint(100, self.max_val * 10)))
            mutation_type.append("Large Text")

        # Random Structure Mutation
        if random_structure:
            for i in range(random.randint(10, self.max_val)):
                additional_tag = f'random_tag_{i}'
                child = SubElement(payload, additional_tag)
                child.text = ''.join(random.choices(string.ascii_letters, k=random.randint(10, self.max_val)))
            mutation_type.append("Random Structure")

        # Invalid Characters Mutation
        if invalid_chars:
            invalid_character = random.choice(['\x00', '\x1F', '\x7F'])
            for elem in payload.iter():
                if elem.text:
                    elem.text += invalid_character
            mutation_type.append("Invalid Characters")

        # Unclosed Tags Mutation
        if unclosed_tags:
            unclosed_elem = Element("unclosed")
            payload.append(unclosed_elem)
            mutation_type.append("Unclosed Tags")

        # Large Attribute List Mutation
        if large_attribute_list:
            for elem in payload.iter():
                for i in range(random.randint(1, 20)):
                    attr_name = f'attr_{i}'
                    attr_value = ''.join(random.choices(string.ascii_letters + string.digits + "\x00", k=random.randint(1, 50)))
                    elem.set(attr_name, attr_value)
            mutation_type.append("Large Attribute List")

        # All Blank Mutation
        if all_blank:
            for elem in payload.iter():
                elem.text = ''
                elem.attrib.clear()
            mutation_type.append("All Blank")

        # Wrong Input Mutation
        if wrong_input:
            for elem in payload.iter():
                if elem.text is not None:
                    if elem.text.isdigit():
                        elem.text = ''.join(random.choices(string.ascii_letters, k=10))
                    else:
                        elem.text = str(random.randint(0, 10000))
            mutation_type.append("Wrong Input")

        mutation_dict = {
            "empty_or_nonxml": empty_or_nonxml,
            "large_text": large_text,
            "random_structure": random_structure,
            "invalid_chars": invalid_chars,
            "unclosed_tags": unclosed_tags,
            "large_attribute_list": large_attribute_list,
            "all_blank": all_blank,
            "wrong_input": wrong_input
        }

        return tostring(payload, encoding="unicode"), mutation_dict

