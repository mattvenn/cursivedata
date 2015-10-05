import matplotlib.pyplot as plt
import csv
import glob

csvfiles = glob.glob('*csv')
for f in csvfiles:
    with open(f) as csvfile:
        steps = []
        diameter = []
        c = csv.reader(csvfile)
        for row in c:
            steps.append(row[0])
            diameter.append(row[1])
        plt.plot(steps,diameter,label=f,linewidth=2)
plt.ylabel('diameter')
plt.xlabel('steps')
legend = plt.legend(loc='upper left')
plt.show()
