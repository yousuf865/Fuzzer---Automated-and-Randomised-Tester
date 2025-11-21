# Assuming your JPEG file is named 'test.jpg'

from jpeg import Jpeg
import os

if not os.path.exists("../../../oskar-smethurst-B1GtwanCbiw-unsplash.jpg"):
    print("Error: Please place a JPEG file named 'test.jpg' in this directory.")
else:
    with open("../../../oskar-smethurst-B1GtwanCbiw-unsplash.jpg", "rb") as f:
        # 1. Load the binary data
        data = f.read()

    # 2. Parse the data using the generated class
    try:
        parsed_file = Jpeg.from_bytes(data)

        print(data)
        
        print("--- JPEG Parsing Successful ---")
        
        # 3. Iterate through all segments (markers) found
        for segment in parsed_file.segments:
            # Note: The exact attributes depend on the jpeg.ksy structure
            segment_name = segment.marker.name
            segment_length = getattr(segment, 'length', 'N/A')
            segment_data = getattr(segment, 'data', 'N/A')
            
            mark = (0xFF << 8) | segment.marker.value
            print(f"[{segment_name}][{hex(mark)}] Length: {segment_length}")
            print(f"[{segment_name}] Data: {segment_data}")

            if segment.marker == 0xc2:
                print(f"num_____: {getattr(segment_data, 'num_components')}")


    except Exception as e:
        print(f"An error occurred during parsing: {e}")
