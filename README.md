# comp6447-fuzzer
Repository for the COMP6447 assignment at UNSW to create a fuzzer. Spec can be found [here](https://fuzzer.6447.lol/spec)
## Due dates:
- **Midpoint check-in:** 25/10/2024
- **Final due date:** 11/11/2024
## Midpoint checkin
- Only csv1 and json1 are tested for checkin

### Example usage:
```bash
gdb --interpreter=mi2 commands.gdb r < outputs/manual_input_payload.txt
```