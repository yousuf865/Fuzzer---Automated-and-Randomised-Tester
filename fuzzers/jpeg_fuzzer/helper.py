import random
import copy
import struct
import string

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mutations import Mutations # i dont know how to import

class JPEG_mutator:

    @staticmethod
    def dht_mutate(dht, mutate_table_id=None, mutate_code_amounts=None):
        indeces = [_ for _ in range(0, len(dht) - 1)]
        
        print('dht tables: ' + str(len(indeces)))
        mutate_amount = random.randint(0, len(dht) - 1)
        for i in range(mutate_amount):
            print(indeces)
            idx = random.choice(indeces)
            indeces.remove(idx)
            
            dht[idx] = JPEG_mutator.huffman_mutate(dht[idx])

        return dht

    #table_data {
    #    'table_type': table_id, 
    #    'code_lengths': code_lengths,
    #    'table': code_table
    #}
    # original_huffman = array of table_data
    @staticmethod
    def huffman_mutate(segment, symbol_num_desync=None, mutate_table_id=None, mutate_code_amounts=None):
        try:
            marker, length, dht, order = segment
        except ValueError:
            marker, length, dht, order, _ = segment

        if not dht:
            return segment

        tables_to_mutate_count = random.randint(0, len(dht))
        indices_to_mutate = random.sample(range(len(dht)), tables_to_mutate_count)

        for idx in indices_to_mutate:
            table_data = dht[idx]
            
            code_values_ba = bytearray(table_data['table']) 
            code_lengths_list = list(table_data['code_lengths'])
            
            code_values_ba = Mutations().bit_flip(
                code_values_ba, 
                random.randint(0, len(code_values_ba) - 1)
            )
            
            if mutate_table_id is True:
                table_data['table_id'] = struct.pack('>B', random.randint(0, 0x1F)) 

            curr_idx = 0

            for i in range(16):
                current_count = code_lengths_list[i]
                
                if random.choice([True, False]):
                    continue
                
                max_subtraction = min(current_count, 5)
                change_amount = random.randint(-max_subtraction, 5) 
                
                if change_amount == 0:
                    continue
                
                curr_idx += code_lengths_list[i]

                if change_amount > 0:
                    new_bytes = bytes([random.randint(0, 0xFF) for _ in range(change_amount)])
                    code_values_ba[curr_idx:curr_idx] = new_bytes 
                else:
                    del code_values_ba[curr_idx + change_amount:curr_idx]
                
                curr_idx += change_amount

                if symbol_num_desync and random.choice([False, True]):
                    continue

                code_lengths_list[i] += change_amount
            
            table_data['code_lengths'] = bytes(code_lengths_list) 
            table_data['table'] = bytes(code_values_ba) 

        return marker, length, dht, order

    # random position of a marker (possibly making it double)
    @staticmethod
    def insert_random_markers(jpg_bytes, segments, marker_mutate_count=None, marker_dup_count=None):
        data = bytearray(jpg_bytes)
        jpg_length = len(data)

        mutate_count = 1 if marker_mutate_count is None else marker_mutate_count

        for i in range(mutate_count):
            marker = random.choice(list(segments.values()))[0][0]
            marker_bytes = struct.pack('>H', marker)

            r = random.randint(0, jpg_length)
            
            data[r:r] = marker_bytes

        return bytes(data)

    @staticmethod
    def marker_mutate(segments, num_to_mutate=None):
        count = num_to_mutate if num_to_mutate else 1
        
        for i in range(count):
            segment_name = random.choice(list(segments.keys()))

            data = segments[segment_name]
            r = random.randint(0, len(data))

    @staticmethod
    def sof_mutate(segment):
        def mutate_data(data):
            if random.choice([True,False]):
                return data
            r = random.randint(0, 10) 

            if random.choice([True,False]):
                ret = data - r
                return ret if ret >= 0 else 1
            else:
                return data + r

        marker, length, data, order = segment
        
        data.bits_per_sample = mutate_data(data.bits_per_sample)
        data.image_height = mutate_data(data.image_height)
        data.image_width = mutate_data(data.image_width)

        #TODO component mutate
        
        return (marker, length, data, order)

    @staticmethod
    def byte_stuffing(image_data, check=None):
        data = bytearray(image_data)

        curr = 0
        while True:
            curr = data.find(b'\xff', curr)
            if curr == -1:
                break
            
            if check is None:
                data.insert(curr + 1, 0x00)
            else:
                if data[curr + 1] != 0x00:
                    data.insert(curr + 1, 0x00)

            curr += 2
        return bytes(data)
    
    @staticmethod
    def sos_mutate(segment, component_mutation=None, keep_byte_stuffing=None): 
        def component_deletion(num,components):
            for i in range(num):
                if not components:
                    break
                idx = random.randint(0, len(components))
                del components[idx]
            return components

        def component_pure_mutation(num):
            components = data.components
            return component_deletion(random.randint(0, len(components)), components)

        def component_sync_mutation(num):
            components = data.components
            return component_deletion(num, components)

        marker, length, data, order, s = segment
        
        if component_mutation and random.choice([False, True]):
            if random.choice([False, True]):
                del data.components[random.randint(0, len(data.components) - 1)]
                data.num_components -= 1
            else:
                data.num_components = random.randint(1, data.num_components + 1)
                if random.choice([False, True]):
                    del data.components[random.randint(0, len(data.components) - 1)]
            
        return (marker, length, data, order, s)
    
    @staticmethod
    def sos_imagedata_mutation(image_data: bytes, cancel_byte_stuffing=None):
        data = bytearray(image_data)
        
        strat = random.choice([Mutations().bit_flip, Mutations().byte_flip])

        data = strat(data, random.randint(0, len(data) // 2))
        
        if cancel_byte_stuffing:
            return bytes(data)

        data = JPEG_mutator.byte_stuffing(data, True)

        return bytes(data)
    
    @staticmethod
    def app0_mutation(segment):
        def _ascii_mutate(data: bytearray, num):
            mutation_pool = string.ascii_letters + string.digits
            random_char = random.choice(mutation_pool)
            random_byte = random_char.encode('ascii')[0]
            index = random.randint(0, len(data) - 1)
            data[index] = random_byte
            return data

        def _random_val(bit_size: int) -> int:
            """Returns a completely random integer value based on bit size (8-bit or 16-bit)."""
            if bit_size == 16:
                return random.randrange(0, 65536)
            else: # 8-bit
                return random.randrange(0, 256)

        def _bitflip_val(value: int, num_bits: int) -> int:
            """Flips a single random bit in an integer value."""
            bit_index = random.randrange(0, num_bits)
            return value ^ (1 << bit_index)

        marker, length, data, order = segment

        if random.choice([False, True]):
            char = random.choice(string.ascii_letters)
            magic = bytearray(data.magic.encode())

            '''
            mutators = [
                Mutations().bit_flip,
                Mutations().byte_flip,
                _ascii_mutate
            ]

            chosen_mutator = random.choice(mutators)
            CANCELED, CUZ MAGIC HAS TO BE STRING SO ONLY ASCII MUTATE
            '''
            magic = _ascii_mutate(magic, 1)

            data.magic = bytes(magic).decode()
        
        """
        Probabilistically and independently mutates core fields of the APP0 segment.
        """
        # List of fields and their sizes in bits
        fields = [
            ('version_major', 8),
            ('version_minor', 8),
            ('density_unit', 8),
            ('density_x', 16),
            ('density_y', 16),
            ('thumbnail_x', 8),
            ('thumbnail_y', 8),
        ]

        for field_name, bit_size in fields:

            # Ensure the object has the field
            if not hasattr(data, field_name):
                continue

            # --- INDEPENDENT PROBABILITY CHECK FOR EACH FIELD ---
            if random.choice([False, True]):

                current_value = getattr(data, field_name)

                # Randomly choose between Bit Flip and Byte Flip
                if random.choice([False, True]):
                    # Bit Flip
                    mutated_value = _bitflip_val(current_value, bit_size)
                else:
                    # Byte Flip (random value assignment)
                    mutated_value = _random_val(bit_size)

                # Assign the mutated value back to the object
                setattr(data, field_name, mutated_value)

        return marker, length, data, order
    
    @staticmethod
    def single_segment_agnostic_mutation(segment: tuple):
        marker, length, data, order = segment   # Order kinda useless here
        
        if marker in (0xffd8, 0xffd9, 0xffe0, 0xffda):
            return None

        # TODO: what about BYTE flip?
        strat = random.choice([Mutations().bit_flip])
    
        mutated_part = strat(bytearray(data), random.randint(0, len(parts[mutate_idx])))
        
        parts[mutate_idx] = mutated_part

        return tuple(parts)
