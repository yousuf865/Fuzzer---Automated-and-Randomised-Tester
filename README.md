# comp6447-fuzzer
Repository for the COMP6447 assignment at UNSW to create a fuzzer. Spec can be found [here](https://fuzzer.6447.lol/spec)
## Due dates:
- **Midpoint check-in:** Week 7 Friday 4pm (Oct 31)
- **Final due date:** Week 10 Friday 4pm (Nov 22)
## Midpoint checkin
- Only csv1 and json1 are tested for midpoint checkin

### Example usage:
```bash
gdb --interpreter=mi2 commands.gdb r < outputs/manual_input_payload.txt
```
