import csv
import os
import argparse
import MySQLdb
import math
from datetime import datetime

import t2c 
import t2d 



def main():
    e=False
    
    while e==False:
        args=input("Choose a task:").split();
        n=len(args)
        if n==1:
            task=args[0]
            if task=="exit":
                e=True
                print("End the program")
                break;
        else: 
            print("invalid input")  
            
    
        
        if task=="task2c":
            t2c.do_t2c()
        elif task=="task2d":
            t2d.do_t2d()
        else:
            print("invalid input")

            
main()