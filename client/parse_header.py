import re

header_file = 'config.h'

def parse_header():
    names = []
    pack = []
    try:
        lines = open(header_file).readlines()
    except IOError:
        print "no such file", header_file
        exit(1)
    for line in lines:
        m = re.search('(int|byte|float)\s(\w+)',line)
        if m:
            #print m.group(1),m.group(2)
            names.append(m.group(2))
            if m.group(1) == 'int':
                pack.append('h')
            elif m.group(1) == 'float':
                pack.append('f')
            elif m.group(1) == 'byte':
                pack.append('B')
            else:
                print "bad type:", m.group(1)
                exit(1)

    return (names,pack)
if __name__ == '__main__':
    print parse_header()
