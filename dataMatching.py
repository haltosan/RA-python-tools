from file_analysis import *


def getColumn(csvFile, key):
    i = 0
    while True:
        col = csvColumn(csvFile, i)
        if col[0] == key:
            return col[1:]
        if i > 1000:
            return None
        i += 1

def matchOnValue(a, b, colKey):
    aCol = getColumn(a, colKey)
    bCol = getColumn(b, colKey)
    for aI in range(len(aCol)):
        for bI in range(len(bCol)):
            if aCol[aI] == bCol[bI]:
                yield a[aI + 1], b[bI + 1]

def fuzzyMatch(a, b, colKey, fuzzyFunction):
    aCol = getColumn(a, colKey)
    bCol = getColumn(b, colKey)
    for aIndex in range(len(aCol)):
        for bIndex in range(len(bCol)):
            if fuzzyFunction(aCol[aIndex], bCol[bIndex]):
                yield a[aIndex + 1], b[bIndex + 1]

'''
>>> a = get('a.csv')
>>> b = get('b.csv')
>>> i = fuzzyMatch(a, b, 'date', lambda x, y: (int(x) - int(y)) < 2)
>>> for x in i:
	print(x)

	
('0,Bill,Nebraska,4', '0,Nebraska,4,blue')
('0,Bill,Nebraska,4', '1,Nebraska,5,red')
('1,Bob,New York,5', '0,Nebraska,4,blue')
('1,Bob,New York,5', '1,Nebraska,5,red')
('2,Joe,California,4', '0,Nebraska,4,blue')
('2,Joe,California,4', '1,Nebraska,5,red')
('3,Fred,Utah,5', '0,Nebraska,4,blue')
('3,Fred,Utah,5', '1,Nebraska,5,red')
('4,Ted,Washington,5', '0,Nebraska,4,blue')
('4,Ted,Washington,5', '1,Nebraska,5,red')

'''
