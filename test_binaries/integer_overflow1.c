#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// A simple program that can test known ints or arithmetic mutation by crashing 
// when a large integer overflows and turns into a negative number
void vuln() {
    int money;
    printf("I've got so much money, I'm feeling generous. How much money do you want?\n");
    scanf("%d", &money);
    printf("I'll do you one better, here's 10 more dollars!\n");
    
    int new_money = money + 10;
    printf("You now have %d dollars!\n", new_money);
    int *buffer = (int *)malloc(new_money);
    memset(buffer, 0, new_money);
}

int main() { 
    vuln(); 
    return 0;
}