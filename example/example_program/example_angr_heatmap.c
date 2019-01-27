// C program for generating a 
// random number in a given range. 
#include <stdio.h> 
#include <stdlib.h> 
#include <time.h> 
  
int main() 
{ 
    int rand_1, rand_2; 
    // Use current time as  
    // seed for random generator 
    srand(time(0)); 
    while(1){
        rand_1 = (rand() % 2000);
        rand_2 = (rand() % 2000);
        if(rand_1 + rand_2 == 1337){
            printf("Success!");
            break;
        }
   }

  
    return 0; 
} 
