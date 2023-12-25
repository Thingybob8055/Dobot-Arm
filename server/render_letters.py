import math
import os
import string
import datetime
import re
import bezier
import numpy as np

MAX_WIDTH = 200
MAX_HEIGHT = MAX_WIDTH/math.sqrt(2)

def render_str(str):
    filter = re.compile('[^A-Za-z ]')
    str = filter.sub('', str)
    if len(str) == 0:
        print("No printable characters provided")
        return
    alphabet = list(string.ascii_uppercase) + [' ']
    symbols = {}
    for letter in alphabet:
        filename = f'font/{letter}.svg'
        if letter==' ':
            filename = 'font/space.svg'
        # print("Loading file:", filename)
        with open(filename, "r") as f:
            content = f.read()
        if len(content) == 0:
            print(f'Could not read {filename}')
            exit()
        path_text = get_svg_path(content)
        symbols[letter] = parse(path_text)
    width = 0
    height = 0
    for letter in str.upper():
        (iwidth, iheight) = symbols[letter].size()
        width += iwidth
        height = max(iheight, height)
    width_scale = MAX_WIDTH/width
    height_scale = MAX_HEIGHT/height
    scale = min(width_scale, height_scale)
    armcode = []
    for letter in str.upper():
        armcode += symbols[letter].armcode(scale)
    armcode = optimize_armcode(armcode)
    dt = datetime.datetime.now()
    output_dir = 'queue'
    filename = f'{output_dir}/{dt.month:02}-{dt.day:02}T{dt.hour:02}-{dt.minute:02}-{dt.second:02} {str}.armcode'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(filename, 'w') as f:
        for line in armcode:
            f.write(line+'\n')
        print(f'Successfully wrote word {str} to {filename}')

def get_svg_path(svg_text):
        path_tag = svg_text.find("<path")
        path_start = svg_text[path_tag:].find('d="')+3+path_tag
        path_end = svg_text[path_start:].find('"')+path_start
        return svg_text[path_start:path_end]

class SVGPoint:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def str_scale(self, scale=1.0):
        return f'{self.x*scale},{self.y*scale}'
    def rel_from(self, other):
        rel_x = self.x - other.x
        rel_y = self.y - other.y
        return SVGPoint(rel_x, rel_y)
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f'{self.x},{self.y}'

class SVGMove:
    def __init__(self, xyPoint):
        self.point = xyPoint
    def armcode(self, scale=1.0):
        return [f'm,{self.point.str_scale(scale)}']
    def size(self):
        return (self.point.x, self.point.y)

class SVGLine:
    def __init__(self, xyPair):
        self.pointList = xyPair
    def armcode(self, scale=1.0):
        move1 = self.pointList[0]
        move2 = self.pointList[1].rel_from(move1)
        return [f'm,{move1.str_scale(scale)}', 'd', f'm,{move2.str_scale(scale)}', 'u']
    def size(self):
        x = self.pointList[2].x
        y = self.pointList[2].y
        return (x, y)

class SVGCurve:
    def __init__(self, xyTriplet):
        points = np.asfortranarray([
            [0] + [point.x for point in xyTriplet],
            [0] + [point.y for point in xyTriplet]
        ])
        self.curve = bezier.Curve(points, degree=3)
    def armcode(self, scale=1.0):
        num_samples = 5
        sample_points = np.linspace(0.0, 1.0, num_samples)
        samples = self.curve.evaluate_multi(sample_points).swapaxes(0,1)
        result = ['d']
        for prev,sample in zip(samples[:-1], samples[1:]):
            x = sample[0] - prev[0]
            y = sample[1] - prev[1]
            result.append(f'm,{x*scale},{y*scale}')
        return result + ['u']
    def size(self):
        end = self.curve.evaluate(1.0)
        x = end[0][0]
        y = end[1][0]
        return (x, y)

class SVGSymbol:
    def __init__(self, svgCmds):
        self.svgCmds = svgCmds
    def size(self):
        x_sum = 0
        y_sum = 0
        x_max = 0
        y_max = 0
        for cmd in self.svgCmds:
            (x,y) = cmd.size()
            x_sum += x
            y_sum += y
            x_max = max(x_sum, x_max)
            y_max = max(y_sum, y_max)
        return (x_max, y_max)
    def _reset_cmd(self, scale=1.0):
        x_sum = 0
        y_sum = 0
        x_max = 0
        for cmd in self.svgCmds:
            (x,y) = cmd.size()
            x_sum += x*scale
            y_sum += y*scale
            x_max = max(x_sum, x_max)
        reset_cmd = f'm,{x_max-x_sum:.2f},{-y_sum:.2f}'
        return reset_cmd
    def armcode(self, scale=1.0):
        result = []
        for cmd in self.svgCmds:
            result += cmd.armcode(scale)
        result += [self._reset_cmd(scale)]
        return optimize_armcode(result)

def svg_command_factory(command, pointList):
    if command=='m' and len(pointList)==1:
        return SVGMove(pointList[0])
    elif command=='l' and len(pointList)==2:
        return SVGLine(pointList)
    elif command=='c' and len(pointList)==3:
        return SVGCurve(pointList)
    else:
        raise ValueError(f"Invalid command format for command {command} with {len(pointList)} arguments")

def pairwise(iterable):
    a = iter(iterable)
    # each access will advance
    return zip(a, a)

def optimize_armcode(armcode):
    norel0 = [x for x in armcode if x!='m,0.0,0.0']
    noud = []
    for a,b in zip(norel0, norel0[1:]+['']):
        if a=='u' and b=='d':
            continue
        noud.append(a)
    norepeat = []
    curpos = 'u'
    for a in noud:
        if a!=curpos:
            norepeat.append(a)
        if a=='u' or a=='d':
            curpos = a
    return norepeat

def parse(path_text):
    commands = re.split("([A-Za-z])", path_text)
    commands = [x for x in commands if x!='']
    svgCmds = []
    for action,value_pairs in pairwise(commands):
        value_pairs = value_pairs.split(" ")
        value_pairs = [x for x in value_pairs if x!='']
        values = []
        for s in value_pairs:
            point_str = s.split(",")
            x = float(point_str[0])
            y = float(point_str[1])
            values.append(SVGPoint(x,y))
        svgCmds.append(svg_command_factory(action,values))
    svgSymbol = SVGSymbol(svgCmds)
    return svgSymbol
    # armcode = svgSymbol.armcode()
    # return armcode
