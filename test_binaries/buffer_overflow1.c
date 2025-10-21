#include <stdio.h>
#include <stdlib.h>

// Simple program where gets() can lead to a buffer overflow attack
void vuln() {
    char buffer[20];
    gets(buffer);
}

int main() {
    vuln();
    return 0;
}