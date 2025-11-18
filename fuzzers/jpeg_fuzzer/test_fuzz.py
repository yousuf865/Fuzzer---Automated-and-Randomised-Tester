from jpeg_fuzzer import JPEGFuzzer

fuzzer = JPEGFuzzer()

fuzzer.take_input('../../../oskar-smethurst-B1GtwanCbiw-unsplash.jpg')

print(fuzzer.segments)
