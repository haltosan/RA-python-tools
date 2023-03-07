PAGE_BREAK_THRESH = 200
CONNECTED_THRESH = 10
APPROX_THRESH = 10
ROW_LENGTH = 1000

VOLUME_NUM = '85'
IMAGE_NUM = '12'

import os
import json



'''              ===labelme points===
order placed

-x-
low -> high

-y-
low  |
high V
'''


'''              ===user instructions===

place the points in the following order: 
3 2 
0 1 

joins then happen between shape[i] and shape[i+1]
 an exception when shape[i] is bottom of page 1 and shape[i+1] is top of page 2 
'''

shapesAdded = 0

def pageBreak(a:[list], b:[list]) -> bool:
    return abs(a[0][1] - b[3][1]) > PAGE_BREAK_THRESH

def connected(a:[list], b:[list]) -> bool:
    return abs(a[0][0] - b[3][0]) <= CONNECTED_THRESH and abs(a[0][1] - b[3][1]) <= CONNECTED_THRESH

def connect(a:dict, b:dict) -> dict:
    global shapesAdded
    a = a['points']
    b = b['points']
    if pageBreak(a,b):
        return False
    if connected(a,b):
        return False
    shapesAdded += 1
    return pointsToShape([b[3],b[2],a[1],a[0]])

def pointsToShape(points:[list]) -> dict:
    return {'label': 'row', 'points': points, 'group_id': None, 'shape_type': 'polygon', 'flags': {}}

def postProcess(shapes:[dict]) -> [dict]:
    out = []
    for i in shapes:
        if i is not False:
            out.append(i)
    return out

def addShapes():
    jsonName = 'record_image_vol_' + VOLUME_NUM + '_num_' + IMAGE_NUM + '.json'

    os.chdir(r'V:\FHSS-JoePriceResearch\papers\current\colorado_land_patents\data\tract books\row from full training')
    j = json.load(open(jsonName,'r'))
    shapes = j['shapes']
    sortedShapes = list()
    for shape in shapes:
        points = shape['points']
        newShape = pointsToShape(sortPoints(points))
        sortedShapes.append(newShape)
    shapes = sortedShapes
    
    newShapes = list()
    for i in range(len(shapes) - 1):
        newShapes.append(shapes[i])
        newShapes.append(connect(shapes[i], shapes[i+1]))
        
    newShapes.append(shapes[-1])
    j['shapes'] = postProcess(newShapes) 
    json.dump(j, open(jsonName,'w'))
    print(shapesAdded, 'shapes added')


def score(points:[[int,int]]) -> [[[int,int],int]]:
    '''find the left most point; find the next leftmost point; compare y values to determine which is top left and bottom left'''
    # leftmost
    minX:int = points[0][0]
    minXI:int = 0
    for i in range(len(points[1:])):
        if points[i][0] < minX:
            minX = points[i][0]
            minXI = i
    # next leftmost
    nextMinXI:int = 0 if minXI != 0 else 1
    nextMinX:int = points[nextMinXI][0]
    for i in range(len(points)):
        if i != minXI and points[i][0] < nextMinX:
            nextMinXI = i
            nextMinX = points[i][0]
    topI = minXI if points[minXI][1] > points[nextMinXI][1] else nextMinXI
    bottomI = nextMinXI if topI == minXI else minXI
    sign:int = bottomI- topI  # +-1
    return [[points[i], (sign)*(topI - i) % len(points)] for i in range(len(points))]
    

def sortPoints(points:[list])->[list]:
    newPoints = score(points)
    newPoints.sort(key = lambda i : i[1])
    return [i[0] for i in newPoints]



addShapes()

