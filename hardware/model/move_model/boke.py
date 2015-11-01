from bokeh.plotting import figure, output_file, show, ColumnDataSource, gridplot
#from bokeh.models import HoverTool, PanTool, WheelZoom
import pickle
from pprint import pprint

with open('points.d') as fh:
    data = pickle.load(fh)
x = []
y = []
for p in data['p']:
    x.append(p['point'][0])
    y.append(p['point'][1])

init_source = ColumnDataSource(
        data=dict(
            x=x,
            y=y,
        )
    )
x = []
y = []
max_spd = []
ltd_spd = []
points = range(len(data['bp']))
    
for p in data['bp']:
    x.append(p['point'][0])
    y.append(p['point'][1])
    max_spd.append(p['max_spd'])
    ltd_spd.append(p['ltd_spd'])

#pprint(data['bp'])
p_source = ColumnDataSource(
        data=dict(
            points=points,
            x=x,
            y=y,
            max_spd=max_spd,
            ltd_spd=ltd_spd,
        )
    )

x = []
y = []
for i in data['i']:
    x.append(i[0])
    y.append(i[1])

i_source = ColumnDataSource(
        data=dict(
            x=x,
            y=y,
        )
    )

"""
hover = HoverTool(
        tooltips=[
          ("index", "$index"),
          ("max spd", "@max_spd"),
        ]
    )
"""
TOOLS = 'wheel_zoom,hover,pan,tap,resize,reset'
# output to static HTML file
output_file("lines.html", title="line plot example")
p1 = figure(plot_width=600, plot_height=600, title="points", tools=TOOLS)
p1.line('x', 'y', line_width=2, source=init_source)
p1.square('x', 'y', source=init_source)

p2 = figure(plot_width=600, plot_height=600, title="segments with max speeds", tools=TOOLS)
p2.line('x', 'y', line_width=2, source=p_source)
p2.square('x', 'y', size=max_spd, source=p_source)

p3 = figure(plot_width=600, plot_height=600, title="max spd & ltd spd against points", tools=TOOLS)
p3.line('points', 'max_spd', line_width=2, source=p_source)
p3.line('points', 'ltd_spd', line_width=2, line_color="red", source=p_source)

p4 = figure(plot_width=600, plot_height=600, title="interpolated points at fixed freq", tools=TOOLS)
p4.line('x','y', line_width=2, source=i_source)
p4.square('x','y', size=4, source=i_source)
# show the results
p = gridplot([[p1, p2],[p3, p4]])
show(p)
