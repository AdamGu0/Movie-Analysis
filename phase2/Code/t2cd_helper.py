import csv
import math
import os



def group_csv_write(file_name,object_name,list,labels):
    csvrows=[]
        
    with open(file_name, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar=' ', quoting=csv.QUOTE_ALL)
        csvrows.append([object_name,'Group'])
        
        for r in range(0,len(list)):
            csvrows.append([list[r],labels[r]+1])
        
        for row in csvrows:
            csvwriter.writerow(row)