#!/usr/bin/env python
import json
import csv
name = "testhist.csv"
with open(name) as fh:
    reader = csv.reader(fh)
    header = reader.next()
    if header[0] != 'time':
        print("need time as first field")
        exit(1)
    #create data structure
    data = {}
    for key in header[1:]:
        data[key] = []
    #for each row in the csv
    for row in reader:
        #for each field in header (apart from time)
        for key in header[1:]:
            data[key].append({ 'at' : row[0], 'value' : row[header.index(key)]})
        print row

name += ".json"
with open(name,'w') as fh:
    json.dump(data,fh)
