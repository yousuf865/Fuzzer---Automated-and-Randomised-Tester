# Group /fuzz/sh's Fuzzer:

This fuzzer automates testing software applications that accept user-supplied files by generating random CSV, JPEG, JSON, plaintext, XML, and PDF input files.

## Group Members (zID)
* z5584560
* z5489321
* z5611448
* z5308790

## Functionality

### Harness

#### run_fuzzer.sh
The run_fuzzer.sh file is the starting point of the program - it sets up a Docker environment in which the fuzzer can run.

#### fuzzer.py
fuzzer.py implements the Fuzzer class. This first generates an input file of the desired type by calling the appropriate fuzzer's methods (CSVFuzzer, JSONFuzzer, etc.).

It then sends this payload to run against the given binary. It also monitors stderr to detect any crashes that may have been caused by this payload, and also the return codes. If it detects a crash, it records the input file (by writing to a bad_{binary_name}.txt file) that caused it to crash, and also the type of crash that occurred. It then generates a summary of the cause of the crash and the type of crash that occurred.

It repeats this process for a predetermined number of times (given as an arg in main.py)

#### main.py
In the file main.py, an instance of the Fuzzer class is created, and each of the binaries in the 'binaries' directory are run against the fuzzer for a predetermined number of times through Fuzzer's methods (defaulted to 1000).

The file also aggregates the errors found in each of the binaries along with the generated summaries of the parameters that caused the crash. It then prints out which binaries were found to crash along with the errors and the summary of the cause.


### Fuzzers
Each filetype that is fuzzed (e.g. CSV, JSON, etc.) has its own file and class.

For example, the file responsible for generating random CSV files is csv_fuzzer.py, and it implements the CSVFuzzer class. The same applies for JPEG, JSON, plaintext, XML, and PDF files.

All of these files are under the 'fuzzers' directory.

Across all these fuzzers, there are mutations which modify the values, fields and types whilst preserving the structure of the file. An example of this is changing CSV delimiters but keeping row/column counts stable.

There are also mutations which violate the format structure of the file. An example of this is a CSV row-length mismatch.

The common mutation strategies that are employed include bit flips, byte flips, known integers that are likely to trigger integer overflow or parser bugs (e.g. 0, -1, 255, INT_MAX, INT_MIN, etc.), and arithmetic strategies that test around these known integers (256, x - 1, x - 8, etc.).

Each fuzzer has configurable toggles that allow bias towards fuzzing the structure or the values of the input file. This is enabled through the mutation_parameters() function in each fuzzer which takes boolean arguments (determined at random) that decide which inherent attributes of the file to mutate. These inherent attributes can be the number of rows, the inclusion of invalid chars (e.g. '\x00'), or the inclusion of a large number.

The inherent attributes of the files are derived from the valid example input provided in the example_inputs directory.

#### csv_fuzzer.py
First, the valid example CSV file is read and its inherent attributes are derived. Then mutations are applied randomly to each of these attributes. Namely, these attributes are
header, num_rows, num_cols, value_type, cell_val_len, and value_type ("str", "int","float", "hex", "bin" etc.).

These attributes are passed in as arguments to the mutation function and are all booleans (except for value_type), and a True value for one of these arguments would mutate this attribute with a random value. Otherwise if it's false, it would just carry the same attribute as the valid example input. The reason it is so is because this would generate a more diverse range of inputs which would cover more code paths and therefore would be likelier to find more vulnerabilities.

#### json_fuzzer.py
Similar to the CSV fuzzer, the JSON fuzzer also reads the valid JSON file and derives its inherent attributes and mutates them randomly. In this case, the attributes are empty_or_nonjson, large_num, large_input, random_structure, invalid_chars, fstring, large_integer_list, all_blank, all_null, and wrong_input.

These attributes are passed in as arguments to the mutation function and are all booleans, and whether it's true of false determines whether this attribute is mutated or not.

#### plaintext_fuzzer.py
The same process of reading the valid input file and deriving attributes is repeated for the plaintext fuzzer. In this case, the attributes are header, num_lines, value_type, input_len, and the value_type ("str", "int","float", "hex", "bin" etc.).

All of these attributes are passed in as arguments to the mutation function and are all booleans except for value_type, and whether it's true of false determines whether this attribute is mutated or not.

#### xml_fuzzer.py
The xml fuzzer follows the same process in deriving attributes from the valid input file. The attributes are empty_or_nonxml, large_text, random_structure, invalid_chars, unclosed_tags, large_attribute_list, all_blank, and wrong_input.

These are all booleans and whether it's true of false determines whether this attribute is mutated or not.

#### jpeg_fuzzer.py
The jpeg fuzzer follows the same process in deriving attributes from the valid input file. 
We use Kaitaistruct in helping us seperate the jpeg markers

The jpeg is first parsed on each markers, put into their own segments and made into a dictionary where the keys are the names of the segments and the values are lists of segment data which has (marker, length, data, order) and for specifically SOS, we have an extra (segment) in it.

The attributes that can be mutated in the mutation_parameters in jpeg_fuzzer are SOF (Start of Frame), SOS (Start of Scan), APP0 segment, the DHT (Define Huffman Table), image data (the compresses image stream), and markers.

These are all booleans and whether it's true of false determines whether this attribute is would have a change to be mutated or not.

In each of these segments, they are further parsed into their seperate structures which are then going to be mutated accordingly. For example, the DHT segment may have the table mutated, the amount of codes changed. Parts that are closely related to each other such as number of components and the components themselves in the SOF segment maybe mutated to be in sync or not, i.e. whether if a component is added the number of components is also increased or not.

Before being sent out, the jpeg is then reconstructed from these segments (might be mutated or not) back into a single file in bytes. 

**JPEG fuzzer files:**
* `Helper.py` the mutation class (JPEG_mutator)
* `Jpeg_parser.py` ==> the parser and reconstructor class
* `Jpeg_fuzzer.py` ==> the integrated fuzzer for jpeg
* `jpeg.ksy` ==> the jpeg parse definition in the kaitaistruct language

## Bugs Our Fuzzer Can Detect
Through the above mentioned mutation strategies, the fuzzer can detect
- Buffer overflows - heap and / or stack
- Out-of-bounds reads
- Use-after-free triggered by malformed data
- Integer overflows
- Type incompatibility errors / undefined behaviours due to it
- Memory allocation that's too large due to large values


## How thefuzzer works
#### General mutation
Initially for each binary the fuzzer runs general mutaions from mutations.py. The no of iterations is equally distributed among all strategies. Although this could have been a bit better by priotising based on the content. Like prioritising known ints and arithmetic mutations for input with predominantly integer values.

#### File Type based mutations
If the program could not be crashed the main fuzzer then moves to file type based muations. Here for each file there are few mutation paramaters as mentioned above. The fuzzer slowly cycles through a combination of all possible mutations. 

For example if a fuzzer has three mutable params then the combination of mutations would look like [(True, True, True), (True, True, False), ... (False, False, False)]

#### Code Coverage
If a certain combination runs into sleep or loop or if the runtime does_not change for a certain number of iteration, the fuzzer moves on to next combination of mutable params

#### Detecting Hang(sleep or loop)
Generally any execution that lasts over 0.5s is considered a hang. If the cpu_time is closer to the wall time, then it is defined as a loop, otherwise it is defined as a sleep. If a program runs into sleep or loop for 20times, the fuzzer moves on to next binary. 

#### Crash detection
Crash is primarily detected through the return code. If it is less than 0, the program is assumed to have crashed. As per faq page -6 SIGABRT is excluded with the exception of stack smash.

#### Logging and Report
During the execution there is a progress bar that displays the percent of progress made
After the execution a report is printed with the following for each bin
* exit_code
* Strategy through which the binary was cracked
* Time (the time of execution of the particular run incase the binary was crashed, otherwise the cumulative fuzz time which would be usually around 54s as it is the max time set for a single binary)
* stderr and stdout (sometimes insight from the fuzzer is printed in one of these)

## Improvements that can be made to the fuzzer
The fuzzer can be improved by employing multithreading (or multiprocessing in python) to speed up the fuzzing process, with which there can be more inputs that are fuzzed into the binaries.

The only effort made to detect coverage is through comparing runtime. Initially we had more ideas here like capturing process memory map, RIP values etc., but unfortunately no time at the end.

There could have also been a way for the fuzzer to learn which values control what in the program. For example, if it's known that a certain JSON key-value determines the length field of a malloc, then we could base our mutations off of that to generate input that's more likely to cause crashes.

We also didn't implement much of the ELF and PDF fuzzers.

## Something awesome
An idea we had for this was to make a GUI that would display to a user the operations of the fuzzer. From this GUI the user can control the fuzzer through a menu, where a choice of mutation strategies are available to choose from, and the attributes to randomise are customisable.

This would also have the option of specifying where the inputs will be taken. In the current fuzzer, it's assumed that the programs will always take input from stdin and this input will be the only thing they take. With this customisation option, it can more closely reflect the real-world complexity of programs that take input at different stages.

These features would make the app highly desirable by all sorts of companies, as a simple GUI frontend can let the clients control the way they want to fuzz test their programs, without having to implement the fuzzing logic themselves.

