#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

int main(void) {
    printf("Starting sleep...\n");
    fflush(stdout);

    srand((unsigned)time(NULL) ^ (unsigned)getpid());

    if (rand() % 2 == 0) {
        printf("Sleeping for 2 seconds...\n");
        fflush(stdout);
        sleep(2);
        printf("Woke up, exiting.\n");
        return 0;
    } else {
        printf("Chosen to loop indefinitely.\n");
        fflush(stdout);
        while (1) {
        }
    }

    return 0;
}
