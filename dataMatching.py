from file_analysis import *
from pandas import to_datetime
from datetime import *

x = open('obit_output-filtered-twoPlus-surname.csv', 'r', encoding='utf-8')
red = x.read()
x.close()
obits = red.split('\n')
del obits[-1]
del red
db = get('database-filtered-twoPlus-surname.csv')
del db[-1]  # last cell is blank
okey = {'Image':0, 'First_Names':1, 'Last_Name':2, 'Death_Date_Day':3, 'Death_Date_Month':4, 'Death_Date_Year':5,
        'Birth_Date_Day':6, 'Birth_Date_Month':7, 'Birth_Date_Year':8, 'Names':9, 'Dates':10, 'Locations':11,
        'Surname_1':12, 'Surname_2':13, 'Surname_3':14, 'First_1':15, 'First_2':16, 'First_3':17}
dkey = {'ID':0, 'birthlikedate':1, 'deathlikedate':2, 'surname':3, 'givenname':4, 'deathlikeplace':5,
        'birthlikeplace':6, 'sex':7, 'fs_url':8, 'firstname':9}
def o(line, key):
    try:
        return csvSplit(line)[okey[key]]
    except IndexError as e:
        print(line, '||', key)
        raise e
    raise Exception("idk how we got here:" + line + '||'+key)
def d(line, key):
    return csvSplit(line)[dkey[key]]

def dYear(dline, oline):
    try:
        dY = to_datetime(d(dline, 'deathlikedate')).year
    except ValueError:
        return False
    oY = int(o(oline, 'Death_Date_Year'))
    return dY==oY
def bYear(dline, oline):
    try:
        dY = to_datetime(d(dline, 'birthlikedate')).year
    except ValueError:
        return False
    oY = int(o(oline, 'Birth_Date_Year'))
    return dY==oY
def surname(dline, oline):
    try:
        dS = d(dline, 'surname')
        oS = o(oline, 'Last_Name')
    except IndexError as e:
        print(dline, '\n', oline, '\n--')
        raise e
    return dS.lower() == oS.lower()
def twoPlus(dline, oline):
    score = 0
    if surname(dline, oline):
            score += 1
    if dYear(dline, oline):
            score += 1
    if bYear(dline, oline):
            score += 1
    return score >= 2
def allThree(dline, oline):
    if not surname(dline, oline):
        return False
    if not dYear(dline, oline):
        return False
    if not bYear(dline, oline):
        return False
    return True

def anySur(dline, oline):
    oS = [o(oline, 'Last_Name').lower(), o(oline, 'Surname_1').lower(), o(oline, 'Surname_2').lower(), o(oline, 'Surname_3').lower()]
    dS = d(dline, 'surname')
    return dS.lower() in oS
def anyGiven(dline, oline):
    dG = d(dline, 'firstname')
    oG = [o(oline, 'First_Names').lower(), o(oline, 'First_1').lower(), o(oline, 'First_2').lower(), o(oline, 'First_3').lower()]
    return dG.lower() in oG
def twoPlusAnyName(dline, oline):
    score = 0
    if anySur(dline, oline):
        score += 1
    if anyGiven(dline, oline):
        score += 1
    if dYear(dline, oline):
            score += 1
    if bYear(dline, oline):
            score += 1
    return score >= 2

def names(dline, oline):
    score = 0
    if anySur(dline, oline):
        score += 1
    if anyGiven(dline, oline):
        score += 1
    return score >= 2

def leftovers(original: list, result: list, uniqueColumn: str = 'ID'):
    """Keep all lines from original that don't match any value from result based on some uniqueColumn. For example, remove all obits that appear in the output based on ID"""
    idSet = set(getColumn(result, uniqueColumn))
    origID = getColumn(original, uniqueColumn)
    for i in range(len(origID)):
        try:
            if origID[i] not in idSet:
                yield original[i + 1]  # account for header being removed
        except IndexError as exception:
            print('i', i, 'origID', len(origID), 'idSet', len(idSet), 'original', len(original), 'result', len(result))
            return

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
    if columnKey == None:
        aColumn = tableA[1:]  # uses entire rows, but removes the header/keys
        bColumn = tableB[1:]
    else:
        aColumn = getColumn(tableA, columnKey)
        bColumn = getColumn(tableB, columnKey)
    outerLen = len(aColumn)
    firstDone = False
    for aIndex in range(len(aColumn)):
        if aIndex == int(outerLen * .25):
            print('1/4 done')
        elif aIndex == int(outerLen * .5):
            print('halfway done')
        elif aIndex == int(outerLen * .75):
            print('3/4 done')
        for bIndex in range(len(bColumn)):
            if matchFunction(aColumn[aIndex], bColumn[bIndex]) == True:
                yield tableA[aIndex + 1], tableB[bIndex + 1]
        if not firstDone:
            print('first iter done')
            firstDone = True

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
    return output

#########################
## DICT BASED MATCHING ##
#########################

def buildDict(keyCol: list, dataCol: list) -> dict:
    """Creates a dictionary that has a key column value correspond to some data column value.
For example, if key=name and data=id, dict['Bob'] would return a set of id's that have the name Bob.
Another use is looking up rows by value. If key=id and data=entireTable, dict[5] would be the rows that have an id of 5"""
    out = dict()
    for i in range(len(keyCol)):
        key = keyCol[i].lower()
        data = dataCol[i].lower()
        if key not in out:
            out[key] = set()
        out[key].add(data)
    return out

def dictMatch(tableA: list, tableB: list, keyA: str, keyB: str, header: list, matchFunction = lambda dbLine, obitsLine: dbLine == obitsLine) -> list:
    out = list()  # matches
    out.append(csvJoin(header))
    
    matchDict = buildDict(getColumn(tableA, keyA), getColumn(tableA, 'ID'))
    fullDict = buildDict(getColumn(tableA, 'ID'), tableA[1:])  # [1:] to remove the header line
    colB = getColumn(tableB, keyB)
    tableB = tableB[1:]  # remove the header line
    mx = len(colB)  # max iterations
    for i in range(len(colB)):
        key = colB[i].lower()
        if not key in matchDict:  # if we can't find it, move on
            continue
        idSet = matchDict[key]  # get the id's for a given key that matches
        for ID in idSet:
            rowB = tableB[i]
            rowA = list(fullDict[ID])[0]  # cast to a list, then use the 1st (and only) element
            
            if matchFunction(rowA, rowB):
                out.append(rowA + ',' + rowB)  # save the matching rows
                
        if i == int(mx * .1):  # progress indication
            print('10% done')
        if i == int(mx * .25):
            print('25% done')
        elif i == int(mx * .5):
            print('50% done')
        elif i == int(mx * .75):
            print('75% done')

    return out

def dictFuzzyMatch(tableA: list, tableB: list, keyA: str, keyB: str, matchFunction = lambda aValue, bValue: aValue == bValue) -> list:
    out = list()
    matchDict = buildDict(getColumn(tableA, keyA), getColumn(tableA, 'ID'))
    fullDict = buildDict(getColumn(tableA, 'ID'), tableA[1:])  # [1:] to remove the header line
    colB = getColumn(tableB, keyB)
    mx = len(colB)
    for i in range(len(colB)):
        for key in matchDict:
            return None


def matchFull(matchFunction = lambda dbLine, obitLine: dbLine == obitLine, saveName = None, dbLeftoverName = None, obitLeftoverName = None):
    if saveName is None:
        saveName = input('Save file name: ')
    if dbLeftoverName is None:
        dbLeftoverName = input('DB leftover name: ')
    if obitLeftoverName is None:
        obitLeftoverName = input('Obit leftover name: ')
        
    matched = dictMatch(db, obits, 'surname', 'Last_Name', tableKeys(db) + tableKeys(obits), matchFunction)
    save(matched, saveName)
    dbLeftover = getAll(leftovers(db, matched, 'ID'))
    obitLeftover = getAll(leftovers(obits, matched, 'Image'))
    save(dbLeftover, dbLeftoverName)
    save(obitLeftover, obitLeftoverName)
    

'''
make db dict based on name
for entry in obit:
    if not in dict : fail
    dbEntry = db[entry.name]
    if dbEntry.dYear == entry.dYear or dbEntry.bYear == entry.bYear:
        MATCH
'''

'''
a = get('test_database.csv')
a[0] = csvJoin(['id'] + tableKeys(a)[1:])
x = open('test_obits.csv')
b = x.read().split('\n'); del x
del a[-1]
del b[-1]
'''

def dictResult(r: list, h: list) -> list:
    out = list()
    out.append(csvJoin(h))
    for i in r:
        out.append(i[0]+','+i[1])
    return out

















