import jpeg_parser

parser = jpeg_parser.JPEGparser()

segments, raw_data = parser.parse('../../example_inputs/jpg1.txt')


print(segments['sos'][0])

with open('test.jpg', 'wb') as pic:
    pic.write(parser.jpeg_constructor(segments))
