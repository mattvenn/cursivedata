class mapping():

    def __init__(self, in_min, in_max, out_min, out_max, limit=True):
        self.in_min = in_min
        self.in_max = in_max
        self.out_min = out_min
        self.out_max = out_max
        self.limit = limit
       
    def map(self, value):
        if self.limit:
            value = self.limit_it(value)
        
        f = float(value - self.in_min) / float(self.in_max - self.in_min)
        mapped = f * (self.out_max - self.out_min) + self.out_min
        return mapped

    def limit_it(self, value):
        if value > self.in_max:
            value = self.in_max
        if value < self.in_min:
            value = self.in_min
        return value

if __name__ == '__main__':
    m = mapping(3, 12, -10, 10)
    for i in range(0, 20):
        print("%3d -> %3d" % (i, m.map(i)))
