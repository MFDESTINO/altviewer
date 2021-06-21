from shapely.geometry import LineString
from shapely.ops import linemerge
import re

def get_value_by_match(line, match):
    return float(line[match.start()+1:match.end()])

def get_layers_from_gcode(gcode_file):
    with open(gcode_file, "r") as f:
        gcode_lines = f.readlines()

    G1 = re.compile("G1")
    G92 = re.compile("G92")
    M82 = re.compile("M82")
    M83 = re.compile("M83")
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
    max_flow = 0
    for line in gcode_lines:
        if M82.match(line):
            absolute = True
        if M83.match(line):
            absolute = False
        if G92.match(line):
            e_match = E.search(line)
            if e_match:
                ei = get_value_by_match(line, e_match)

        if G1.match(line):
            x_match = X.search(line)
            y_match = Y.search(line)
            z_match = Z.search(line)
            e_match = E.search(line)
            f_match = F.search(line)
            if x_match:
                x = get_value_by_match(line, x_match)
            if y_match:
                y = get_value_by_match(line, y_match)
            if z_match:
                z = get_value_by_match(line, z_match)
                if not z in layers.keys():
                    layers[z] = {"segments": [],
                                   "flows": [],
                                   "speeds": []}
            if e_match:
                e = get_value_by_match(line, e_match)
                if absolute:
                    de = e - ei
                else:
                    de = e
                ei = e
            if f_match:
                f = get_value_by_match(line, f_match)

            if de > 0:
                segment = LineString([(xi, yi), (x, y)])
                if segment.length > 0:
                    flow = de / segment.length
                    if flow > max_flow:
                        max_flow = flow
                else:
                    flow = 0
                layers[z]["segments"].append(segment)
                layers[z]["flows"].append(flow)
                layers[z]["speeds"].append(f)
            xi = x
            yi = y
            de = 0
        layers_props = { "max_flow": max_flow}
    return layers, layers_props
