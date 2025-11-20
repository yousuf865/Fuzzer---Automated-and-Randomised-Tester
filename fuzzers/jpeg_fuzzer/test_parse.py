import jpeg_parser

parser = jpeg_parser.JPEGparser()

segments, raw_data = parser.parse('../../../oskar-smethurst-B1GtwanCbiw-unsplash.jpg')


print(segments['sos'][0])

with open('test.jpg', 'wb') as pic:
    pic.write(parser.jpeg_constructor(segments))
