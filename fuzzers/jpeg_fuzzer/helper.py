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

        for i in range(random.randint(0, len(dht))):
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
    def huffman_mutate(segment, mutate_table_id=None, mutate_code_amounts=None):
        marker, length, data, order = segment

        dht = data
        

        # --------------------------------- Mutate table ------------------------------
        # randomise tables to mutate
        tables_to_mutate = []
        r = random.randint(0, len(dht))
        for i in range(r):
            tables_to_mutate.append(dht[random.randint(0, len(dht) - 1)])

        # mutate table
        for table_data in tables_to_mutate:
            table = table_data['table']
            strategies = [Mutations().bit_flip]
            strat = random.choice(strategies)

            # TODO: what about BYTE flip?
            table = Mutations().bit_flip(bytearray(table), random.randint(0, len(table)))
            table_data['table_id'] = random.randint(0,32)

            table_bit_idx = 0
            for i in range(0, 16):
                random_boolean = random.choice([True, False])
                 
                table_bit_idx += table_data['code_lengths'][i] 
                
                # the amount of code of length i to be added, right now only up to 5 additions
                add_code_num = random.randint(0, 5) if random_boolean else 0
                
               
                if random.choice([True, False]):
                    # if here then code num not done anything to
                    continue
                # randomise minus or not (addition can be minus as well right :P)
                # forgive bad variable name
                add_code_num *= -1 if random.choice([True, False]) else 1
                
                if add_code_num >= 0:
                    addition_bits = [random.choice([0, 1]) for _ in range(add_code_num)]
                    
                    table = table[:table_bit_idx] + addition_bits + table[table_bit_idx:]
                    
                    # adjust index after addition to still be on current index
                    table_bit_idx += add_code_num
                    table_data['code_lengths'][i] += add_code_num
                else:
                    table_bit_idx -= add_code_num

                    table = table[:table_bit_idx] + table[table_bit_idx:]
                    table_data['code_lengths'][i] -= add_code_num

        return marker, length, dht, order



    # random position of a marker (possibly making it double)
    @staticmethod
    def insert_random_markers(jpg_bytes, marker_dup_count=None):
        data = bytearray(jpg_bytes)

        mutate_count = 1 if marker_mutate_count is None else marker_mutate_count

        for i in range(mutate_count):
            marker = random.choice(list(self.markers.values()))[0]
            marker_bytes = struct.pack('>H', marker)

            r = random.randint(0, jpg_length)
            
            data.insert(r, marker_bytes[0])
            data.insert(r + 1, marker_bytes[1])

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
                return ret if ret <= 0 else 1
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
