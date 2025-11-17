from jpeg import Jpeg

import struct

class JPEGparser:
    def __init__(self):
        self.markers = {}
        #self.markers = {
        #    'tem': [],         # 0x01
        #    'sof0': [],        # 0xc0 # start of frame 0
        #    'sof1': [],        # 0xc1 # start of frame 1
        #    'sof2': [],        # 0xc2 # start of frame 2
        #    'sof3': [],        # 0xc3 # start of frame 3
        #    'dht': [],         # 0xc4 # define Huffman table
        #    'sof5': [],        # 0xc5 # start of frame 5
        #    'sof6': [],        # 0xc6 # start of frame 6
        #    'sof7': [],        # 0xc7 # start of frame 7
        #    'soi': [],         # 0xd8 # start of image
        #    'eoi': [],         # 0xd9 # end of image
        #    'sos': [],         # 0xda # start of scan
        #    'dqt': [],         # 0xdb # define quantization table
        #    'dnl': [],         # 0xdc # define number of lines
        #    'dri': [],         # 0xdd # define restart interval
        #    'dhp': [],         # 0xde # define hierarchical progression
        #    'app0': [],        # 0xe0
        #    'app1': [],        # 0xe1
        #    'app2': [],        # 0xe2
        #    'app3': [],        # 0xe3
        #    'app4': [],        # 0xe4
        #    'app5': [],        # 0xe5
        #    'app6': [],        # 0xe6
        #    'app7': [],        # 0xe7
        #    'app8': [],        # 0xe8
        #    'app9': [],        # 0xe9
        #    'app10': [],       # 0xea
        #    'app11': [],       # 0xeb
        #    'app12': [],       # 0xec
        #    'app13': [],       # 0xed
        #    'app14': [],       # 0xee
        #    'app15': [],       # 0xef
        #    'com': [],         # 0xfe # comment
        #}    

    def parse(self, file_path: str) -> dict:
        with open(file_path, 'rb') as file:
            data = file.read()

        try:
            parsed = Jpeg.from_bytes(data)
            print('--- JPEG parsed ---')

            for order, segment in enumerate(parsed.segments):
                segment_name = segment.marker.name
                segment_data = getattr(segment, 'data', None)
                segment_length = getattr(segment, 'length', None)
                full_marker = (0xff << 8) | segment.marker.value
                self.markers.setdefault(segment_name,[]).append((full_marker, segment_length, segment_data, order, segment))

            return self.markers
        except Exception as e:
            print(f"An error occured during Parsing: {e}")

    # Parse Huffman Table
    def dht_table_parse(self, dht_elem: tuple) -> list:
        dht_data = dht_elem[1]
        
        table_data = []
         
        curr = 0
        while curr < len(dht_data):
            curr_table = dht_data[curr:]
            table_id = curr_table[:1]
            code_lengths = curr_table[1: 17]

            table_length = sum(code_lengths)
            code_table = curr_table[17: table_length + 17]
            table_data.append({
                'table_id': table_id, 
                'code_lengths': code_lengths,
                'table': code_table
            })

            curr += table_length + 17
        return table_data

    def dqt_parse(self, segment: tuple):
        data = segment[2]

        # bit 0..3: number of QT (0..3, otherwise error) bit 4..7: the precision of QT, 0 = 8 bit, otherwise 16 bit
        QT_info = data[0] 

        QT_bytes = data[1:]

        return QT_info, QT_bytes

    def SOF_parse(self, segment: tuple):
        data = segment[2]

        data_precision = data[0]
        image_height = data[1:3]
        image_width = data[3:5]
        num_components = data[5:6]
        components = []

        curr = 6
        for i in range(num_components):
            component = data[curr : curr + 3]
            components.append(component)
            curr += 3
        return data_precision, image_height, image_width, num_components, components

    def app0_reconsutrction(self, marker_val, length, data):
        raw_segment = struct.pack('>HH', marker_val, length)
        raw_segment += struct.pack(
            '> 5s B B B H H B B',
            data.magic,                        # 5s: b'JFIF\x00' (Assuming it's b'JFIF\x00')
            data.version_major,                # B: 1 byte
            data.version_minor,                # B: 1 byte
            data.density_unit,                 # B: 1 byte
            data.density_x,                    # H: 2 bytes
            data.density_y,                    # H: 2 bytes
            data.thumbnail_x,                  # B: 1 byte
            data.thumbnail_y                   # B: 1 byte
        )
        
        # TODO thumbnail field parse

        return raw_segment

    def SOS_header_reconstruction(self, marker_val, length, data):
        raw_segment = struct.pack('>HH', marker_val, length)
        raw_segment += struct.pack('>B', data.num_components)
        
        # FOR SOS PROBABLY JUST KEEP THE NUM_COMPONENTS AND COMPONENTS SYNCED UP
        for i in range(data.num_components):
            raw_segment += struct.pack('>BB', data.components[i].id, data.components[i].huffman_table)
        
        raw_segment += struct.pack(
            '>BBB', 
            data.start_spectral_selection
            data.end_spectral
            data.appr_bit_pos
        )

        return raw_segment
    
    def byte_stuffing(self, image_data):
        data = bytearray(image_data)

        curr = 0
        while True:
            curr = data.find(b'\xff', curr)
            if curr == -1:
                break

            data.insert(curr + 1, 0x00)

            curr += 2
        return bytes(data)

    # Remake the jpeg
    # --------------------
    # Current syntax of segments are (length, data, order)
    def jpeg_constructor(self, segments_set) -> bytes:

        # --- 1. Order Segments ---
        segments_ordered = []
        for segment_list in self.markers.values():
            segments_ordered.extend(segment_list)

        # Sort based on the 'order' index (the 4th element: x[3])
        # Note: I changed the index from your original x[2] to x[3] based on your tuple structure (marker, length, data, order)
        segments_ordered.sort(key=lambda x: x[3])

        # --- 2. Prepare (Stuff Bytes and Recalculate Lengths) ---
        reconstructed_segments = []

        for marker_val, length, data_payload, order, segment in segments_ordered:

            processed_data = data_payload

            # SOI (FF D8) and EOI (FF D9) have no length/data fields
            if marker_val in (0xffd8, 0xffd9):
                raw_segment = struct.pack('>H', marker_val) # Write 2-byte marker

            # All other segments require Marker + Length + Data
            elif marker_val not in (0xFFDA, 0xffe0): # Don't reconstruct SOS here since it's the raw data

                # Length value = (Payload size + 2 bytes for the length field itself)
                length_value = length
                
                print('data: ')
                print(processed_data)
                raw_segment = struct.pack('>H', marker_val)
                raw_segment += struct.pack('>H', length_value) # Write 2-byte Big-Endian Length
                raw_segment += processed_data                  # Write Data Payload
            
            elif marker_val == 0xffe0:
                raw_segment = app0_reconstruction(marker_val, length, data_payload)

            elif marker_val == 0xFFDA:
                raw_segment = SOS_header_reconstruction(marker_val, length, data_payload)
                raw_segment += byte_stuffing(segment.image_data)

            reconstructed_segments.append(raw_segment)
        
        # --- 4. Final Output ---
        return b"".join(reconstructed_segments)
