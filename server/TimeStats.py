import time
class TimeStats():
    def __init__(self):
        print "init timestats"
        self.times = []

    #pass unix seconds since epoch
    def addTime(self,seconds=None):
        if seconds == None:
            seconds = int(time.strftime("%s",time.gmtime()))

        self.times.append(seconds)

    def howMany(self,seconds):
        count = 0
        now = int(time.strftime("%s",time.gmtime()))

        length = len(self.times)
        for i in range(length):
            if self.times[i] > now - seconds:
                count += 1

        #remove old items
        self.times = self.times[length-(i+1):length]
            
        return count


