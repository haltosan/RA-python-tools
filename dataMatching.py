from file_analysis import *


def getColumn(table: list, key: str) -> list:
    """Get a column from a csv file (as produced by file_analysis.get(fname))"""
    keys = tableKeys(table)
    try:
        i = keys.index(key)
        return csvColumn(table, i)[1:]  # the first value is the key value
    except ValueError:
        return None

def matchOnValue(tableA: list, tableB: list, columnKey: str) -> tuple:
    """Generator. Returns the rows that match in some column in both csv files (file_analysis.get('foo.csv')) in the form (rowA, rowB)"""
    aColumn = getColumn(tableA, columnKey)
    bColumn = getColumn(tableB, columnKey)
    for aIndex in range(len(aColumn)):  # compare each value from column a with each value of column b
        for bIndex in range(len(bColumn)):
            if aColumn[aIndex] == bColumn[bIndex]:  # compare column a with column b to see if they match exactly
                yield tableA[aIndex + 1], tableB[bIndex + 1]  # 1 is added because the getColumn functions remove the first value (column key) when they return

def fuzzyMatch(tableA: list, tableB: list, columnKey: str, matchFunction) -> tuple:
    """Generator. Same as match on value but uses matchFunction to determine if 2 values match"""
    aColumn = getColumn(tableA, columnKey)
    bColumn = getColumn(tableB, columnKey)
    for aIndex in range(len(aColumn)):
        for bIndex in range(len(bColumn)):
            if matchFunction(aColumn[aIndex], bColumn[bIndex]) == True:
                yield tableA[aIndex + 1], tableB[bIndex + 1]

def join(tableA: list, tableB: list, columnKey: str, matchFunction = lambda x,y : x == y, reason: str = None) -> list:
    """Combine 2 tables if they match on some column value"""
    matches = []
    if reason == None:
        matches.append(csvJoin( tableKeys(tableA) + tableKeys(tableB)))
        for match in fuzzyMatch(tableA, tableB, columnKey, matchFunction):
            matches.append(match[0] + ',' + match[1])
    else:
        matches.append(csvJoin( tableKeys(tableA) + tableKeys(tableB) + ['reason']))
        for match in fuzzyMatch(tableA, tableB, columnKey, matchFunction):
            matches.append(match[0] + ',' + match[1] + ',' + reason)
            
    return matches
    

def tableKeys(table: list) -> list:
    """Returns the key values from a csv file"""
    return csvSplit(table[0])

def project(table: list, newHeader: list) -> list:
    """Change column ordering to match the new header"""
    transpose = []
    for key in newHeader:
        transpose.append(getColumn(table, key))  # add the columns of interest as a row
    
    outTable = []
    outTable.append(csvJoin(newHeader))  # set the header
    for rowIndex in range(len(transpose[0])):  # rotate the table
        row = []
        for columnIndex in range(len(transpose)):
            row.append(transpose[columnIndex][rowIndex])
        outTable.append(csvJoin(row))
    return outTable

def projectNumerical(table: list, newHeader: list) -> list:
    """Project using a numerical header of column numbers"""
    transpose = []
    for i in newHeader:
        transpose.append(csvColumn(table, i)[1:])  # exclude the key value from the column

    # calculate the new header
    outTable = []
    oldHeader = tableKeys(table)
    newHeaderString = []
    for i in newHeader:
        newHeaderString.append(oldHeader[i])
    newHeaderString = csvJoin(newHeaderString)
    outTable.append(newHeaderString)

    for rowIndex in range(len(transpose[0])):
        row = []
        for columnIndex in range(len(transpose)):
            row.append(transpose[columnIndex][rowIndex])
        outTable.append(csvJoin(row))
    return outTable

def matchingColumns(table: list, column1: int, column2: int) -> list:
    """Generator. Filters rows where table[column1] == table[column2]"""
    for row in table:
        splitRow = csvSplit(row)
        if splitRow[column1] == splitRow[column2]:
            yield row

def getAll(generator) -> list:
    """Return all generated values from a given generator"""
    output = []
    for item in generator:
        output.append(item)
    return out

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
