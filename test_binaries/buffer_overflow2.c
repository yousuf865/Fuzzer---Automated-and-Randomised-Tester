#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// A little more complex program that still uses gets() to lead to a buffer overflow attack
void vuln() {
    char buffer[20];
    printf("Correct! What's your favourite fruit?\n");
    gets(buffer);
}

int main() {
    char answer[20];

    printf("Can you guess my favourite fruit?\n");
    scanf("%s", answer);
    getchar(); 

    if (strcmp(answer, "apple") == 0) {
        vuln();
    }

    return 0;
}