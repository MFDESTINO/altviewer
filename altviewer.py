#!/usr/bin/env python3
import matplotlib.pyplot as plt
from import_gcode import get_layers_from_gcode
from matplotlib import cm
from matplotlib.widgets import Button
from shapely.geometry import LineString
from shapely.ops import linemerge
import re
import sys

gcode_file = sys.argv[1]



layers, layers_props = get_layers_from_gcode(gcode_file)

def normalize(values, i):
    return ((values[i])/(layers_props["max_flow"]))

ax = plt.subplot()
plt.subplots_adjust(bottom=0.2)
cmap = cm.get_cmap('Blues', 24)
heights = list(layers.keys())
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

class Index:
    ind = 0

    def next(self, event):
        if self.ind < len(heights) - 1:
            self.ind += 1
        height = heights[self.ind]
        ax.clear()
        paths = layers[height]["segments"]
        flows = layers[height]["flows"]
        ax.set_title(gcode_file)
        ax.text(0.05, 0.95, "z = {}".format(height), transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)
        for i in range(len(paths)):
            x, y = paths[i].xy
            ax.plot(x, y, color=cmap(normalize(flows, i)), linewidth=4)
        plt.draw()

    def prev(self, event):
        if self.ind > 0:
            self.ind -= 1
        height = heights[self.ind]
        ax.clear()
        paths = layers[height]["segments"]
        flows = layers[height]["flows"]
        ax.set_title(gcode_file)
        ax.text(0.05, 0.95, "z = {}".format(height), transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)
        for i in range(len(paths)):
            x, y = paths[i].xy
            ax.plot(x, y, color=cmap(normalize(flows, i)), linewidth=4)
        plt.draw()

callback = Index()
axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bnext = Button(axnext, 'Next')
bnext.on_clicked(callback.next)
bprev = Button(axprev, 'Previous')
bprev.on_clicked(callback.prev)

height = heights[0]
paths = layers[height]["segments"]
flows = layers[height]["flows"]
ax.text(0.05, 0.95, "z = {}".format(height), transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
for i in range(len(paths)):
    x, y = paths[i].xy
    ax.plot(x, y, color=cmap(normalize(flows, i)), linewidth=4)

ax.axis('equal')
ax.set_title(gcode_file)
plt.show()
