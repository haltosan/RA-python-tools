from file_analysis import *


def getColumn(csvFile: list, key: str) -> list:
    """Get a column from a csv file (as produced by file_analysis.get(fname))"""
    i = 0
    while True:
        col = csvColumn(csvFile, i)
        if col[0] == key:  # checks the first value of the row to see if it matches the column key exactly
            return col[1:]
        if i > 1000:  # some arbitrary value to indicate we haven't reached a column with that value because csvColumn will always return something
            return None
        i += 1

def matchOnValue(tableA: list, tableB: list, columnKey: str) -> tuple:
    """Generator. Returns the rows that match in some column in both csv files (file_analysis.get('foo.csv')) in the form (rowA, rowB)"""
    aColumn = getColumn(tableA, columnKey)
    bColumn = getColumn(tableB, columnKey)
    for aIndex in range(len(aColumn)):  # compare each value from column a with each value of column b
        for bIndex in range(len(bColumn)):
            if aColumn[aIndex] == bColumn[bIndex]:  # compare column a with column b to see if they match exactly
                yield tableA[aIndex + 1], tableB[bIndex + 1]  # 1 is added because the getColumn functions remove the first value (column key) when they return

def fuzzyMatch(tableA: list, tableB: list, columnKey: str, matchFunction) -> tuple:
    """Generator. Same as match on value but uses fuzzyFunction to determine if 2 values match"""
    aColumn = getColumn(tableA, columnKey)
    bColumn = getColumn(tableB, columnKey)
    for aIndex in range(len(aColumn)):
        for bIndex in range(len(bColumn)):
            if matchFunction(aColumn[aIndex], bColumn[bIndex]) == True:
                yield tableA[aIndex + 1], tableB[bIndex + 1]

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
