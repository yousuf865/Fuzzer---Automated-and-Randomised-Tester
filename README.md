# Fuzzer - Automated and Randomised Testing
This fuzzer automates testing software applications that accept user-supplied files by generating random CSV, JPEG, JSON, plaintext, and XML input files.

## Bugs Our Fuzzer Can Detect
Through the above mentioned mutation strategies, the fuzzer can detect:
- Buffer overflows - heap and / or stack
- Out-of-bounds reads
- Use-after-free triggered by malformed data
- Integer overflows
- Type incompatibility errors / undefined behaviours due to it
- Memory allocation that's too large due to large values

#### Logging and Report
During the execution there is a progress bar that displays the percent of progress made
After the execution a report is printed with the following for each bin
* exit_code
* Strategy through which the binary was cracked
* Time (the time of execution of the particular run incase the binary was crashed, otherwise the cumulative fuzz time which would be usually around 54s as it is the max time set for a single binary)
* stderr and stdout (sometimes insight from the fuzzer is printed in one of these)

### Example usage:
```bash
gdb --interpreter=mi2 commands.gdb r < outputs/manual_input_payload.txt
```
