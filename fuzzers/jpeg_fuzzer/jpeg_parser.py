from jpeg import Jpeg

class JPEGparser:
    def _init_(self):
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

            for segment in parsed.segments:
                segment_name = segment.marker.name
                segment_data = getattr(segment, 'data', None)
                segment_length = getattr(segment, 'length', None)
                self.markers.setdefault(segment_name,[]).append((segment_length, segment_data))

            return self.markers
        except Exception as e:
            print(f"An error occured during Parsing: {e}")

    # Parse Huffman Table
    def dht_table_parse(self, dht_elem->tuple) -> list:
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

