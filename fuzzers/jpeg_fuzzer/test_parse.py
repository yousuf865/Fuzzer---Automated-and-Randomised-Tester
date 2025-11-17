import jpeg_parser

parser = jpeg_parser.JPEGparser()

segments = parser.parse('../../../oskar-smethurst-B1GtwanCbiw-unsplash.jpg')

with open('test.jpg', 'wb') as pic:
    pic.write(parser.jpeg_constructor(segments))
