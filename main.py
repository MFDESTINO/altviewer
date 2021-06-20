#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib import cm
from shapely.geometry import LineString
from shapely.ops import linemerge
import re

gcode_file = "nicoletti_teste2_e40.gcode"
gcode_file = "f35.gcode"


def get_by_match(line, match):
    return float(line[match.start()+1:match.end()])

def normalize(values, i):
    return ((values[i] - min(values))/(max(values) - min(values)))

with open(gcode_file, "r") as f:
    gcode_lines = f.readlines()

G1 = re.compile("G1")
G92 = re.compile("G92")
G90 = re.compile("G90")
G91 = re.compile("G91")
X = re.compile("X[-]*[\d]+.[\d]+")
Y = re.compile("Y[-]*[\d]+.[\d]+")
Z = re.compile("Z[-]*[\d]+.[\d]+")
E = re.compile("E[-]*[\d]+.[\d]+")
F = re.compile("F[-]*[\d]+.[\d]+")

x, y, z, e, f = 0, 0, 0, 0, 0
xi, yi, zi, ei = 0, 0, 0, 0
de = 0
layers = {}
absolute = True
for line in gcode_lines:
    if G90.match(line):
        absolute = False
    if G91.match(line):
        absolute = True
    if G92.match(line):
        e_match = E.search(line)
        if e_match:
            ei = get_by_match(line, e_match)
            
    if G1.match(line):
        x_match = X.search(line)
        y_match = Y.search(line)
        z_match = Z.search(line)
        e_match = E.search(line)
        f_match = F.search(line)
        if x_match:
            x = get_by_match(line, x_match)
        if y_match:
            y = get_by_match(line, y_match)
        if z_match:
            z = get_by_match(line, z_match)
            if not z in layers.keys():
                layers[z] = {"segments": [],
                               "flows": [], 
                               "speeds": []}
        if e_match:
            e = get_by_match(line, e_match)
            if absolute:
                de = e - ei
            else:
                de = e
            ei = e
        if f_match:
            f = get_by_match(line, f_match)
        if de > 0:
            segment = LineString([(xi, yi), (x, y)])
            if segment.length > 0:
                flow = de / segment.length
            else:
                flow = 0
            layers[z]["segments"].append(segment)
            layers[z]["flows"].append(flow)
            layers[z]["speeds"].append(f)
        xi = x
        yi = y
        de = 0
ax = plt.subplot()
cmap = cm.get_cmap('plasma', 24)

height = list(layers.keys())[0]
paths = layers[height]["segments"]
flows = layers[height]["flows"]
for i in range(len(paths)):
    x, y = paths[i].xy
    ax.plot(x, y, color=cmap(normalize(flows, i)), linewidth=4)

'''
only_paths = []
for path, flow in paths:
    only_paths.append(path)
continuous_paths = linemerge(only_paths)
if type(continuous_paths) == LineString:
    continuous_paths = [continuous_paths]
else:
    continuous_paths = list(continuous_paths)

for path in continuous_paths:
    x, y = path.xy
    ax.plot(x, y, linewidth=2)
'''

ax.axis('equal')
plt.show()
        

