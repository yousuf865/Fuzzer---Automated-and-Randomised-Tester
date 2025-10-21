#include <stdio.h>

// Code taken from 'src2.c' from wargames, 
// but used different numbers to try to make it not the exactly the same
// Program that if given a large input that can integer overflow, can cause read()
// to read more bytes than the size of storage and lead to a buffer overflow attack
int main() {
  char storage[32];

  int bananas = 4;
  int answer;
  printf("You have 4 bananas and I've got 12 left. How many more do you want?\n");
  scanf("%d", &answer);

  if (bananas + answer > 16) {
    printf("Nope, that's too many\n");
    return 1;
  }

  read(0, storage, bananas + answer);
}