from file_analysis import *
pwd = r'C:\Users\esimmon1\Desktop\minerva'
os.chdir(pwd)

raw = get('exported.csv')
rawDates = csvColumn(raw, 1, True)[1:]  # remove column name

dateSplitRegex = r'(?P<birth>.*)((—)|(–)|(-)|(−))(?P<death>.*)'
splitInfo = []
missedLines = []
for line in rawDates:
    collection = collect(line, dateSplitRegex)
    splitInfo.append(collection[0])
    missedLines.append(collection[1])

'''
results so far:
    -total lines in csv : 29,167
    -total missed       : 5,080 | 17% of total

input classes:
    -has 'died' : 126   | 2% of missed
    -has ';'    : 282   | 6% of missed [not easily usable]
    -has 'born' : 4,796 | 94% of missed
    
    -'born', 'died', no ';'    : 40   | < 1% of born
    -'born', 'died', ';'       : 53   | 1% of born
    -'born', no 'died', ';'    : 197  | 4% of born
    -'born', no 'died', no ';' : 4506 | 94% of born
'''

# the plan is to go for the largest gains. here, it's the 'born' class of inputs
# we need to parse more specific cases (born and died) before general cases (born)
# if we don't, we risk missing the death information in the specific case

bornDiedRegex = r'.*born(?P<born>.+)died(?P<died>.+)'  # the (born,died) and (born,died,;) cases
bornDiedSplitInfo = []
bornDiedMissed = []
for line in missedLines:
    collection = collect(line, bornDiedRegex)
    bornDiedSplitInfo.append(collection[0])
    bornDiedMissed.append(collection[1])

# for the rest of the 'born' class, we can just check to see if 'born' is in the line
# if it doesn't, assume it doesn't have useable information

bornSplitInfo = []
bornMissed = []
for line in bornDiedMissed:
    if len(line) > 0 and 'born' in line[0]:
        bornSplitInfo.append([[line[0], '']])
        bornMissed.append([])
    else:
        bornMissed.append([line])
        bornSplitInfo.append([])

# we have data split up into 3 different lists, all containing partial information
# i think of this like a cache system: lookup in the first table, if it's not there, lookup in the next, etc.
def cacheSearch(i, lists):
    for lst in lists:
        n = lst[i]
        if len(n) > 0 and len(n[0]) > 1:
            return n
    return None
allInfo = [splitInfo, bornDiedSplitInfo, bornSplitInfo]


def dateSave():
    # we can move onto extracting dates from the birth/death information above
    # we'll run the same processing on the just birth information

    # this is a rather long regex to capture the various date formats
    #   Year, Day Month Year, Month Day Year
    dateRegex = r'.*?(?P<date>(\d{1,2} ((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{4})|(((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{1,2},? \d{4})|(\d{4})).*'

    birthDates = []
    missedBirthDates = []
    deathDates = []
    missedDeathDates = []
    for i in range(len(splitInfo)):
        line = cacheSearch(i, allInfo)
        if line is not None:
            line = line[0]
            birthCollection = collect(line[0], dateRegex)
            birthDates.append(birthCollection[0])
            missedBirthDates.append(birthCollection[1])

            deathCollection = collect(line[1], dateRegex)
            deathDates.append(collection[0])
            missedDeathDates.append(collection[1])
        else:
            birthDates.append('')
            missedBirthDates.append('')
            deathDates.append('')
            missedDeathDates.append('')

    # at this point, we have the dates for just about all lines (missed 3028 lines, 10%) 

    # the "'"+i[0][0] is to make sure excel doesn't mess with the data (') and is meant to extract just the string ([0][0])
    # the type and length check is to make sure we skip blank lines ([] or ' ')
    readableFormat = lambda lst : ["'"+i[0][0] if type(i) is list and len(i) > 0 else ' ' for i in lst]
    save(readableFormat(birthDates), 'bdates.csv', True)
    save(readableFormat(deathDates), 'ddates.csv', True)


# def location():

# now that we have the information split out, we can start pulling out location
# the first easy case is "such and such was born January 1, 1987 in Townsville, SomeState"
# the key here is the ' in '
inRegex = r'.*? in (?P<location>.+)'
birthLocation = []
missedBirthLocation = []
deathLocation = []
missedDeathLocation = []

for i in range(len(splitInfo)):
    line = cacheSearch(i, allInfo)
    if line is not None:
        line = line[0]
        bCollect = collect(line[0], inRegex)
        birthLocation.append(bCollect[0])
        missedBirthLocation.append(bCollect[1])
        
        dCollect = collect(line[1], inRegex)
        deathLocation.append(dCollect[0])
        missedDeathLocation.append(dCollect[1])
    else:
        birthLocation.append('')
        missedBirthLocation.append('')
        deathLocation.append('')
        missedDeathLocation.append('')

prefixDateRegex = r'.*?(?P<location>([A-Z][A-Za-z]+ ?)+).*?((\d{1,2} ((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{4})|(((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{1,2},? \d{4})|(\d{4})).*'
postfixDateRegex = r'.*?((\d{1,2} ((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{4})|(((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{1,2},? \d{4})|(\d{4})).*?(?P<location>([A-Z][A-Za-z]+ ?)+).*'
preBLoc = []
misPreBLoc = []
preDLoc = []
misPreDLoc = []
for i in range(len(missedBirthLocation)):
    bLine = missedBirthLocation[i]
    dLine = missedDeathLocation[i]
    if type(bLine) is list and len(bLine) > 0:
        preCollect = collect(bLine[0], prefixDateRegex)
        preBLoc.append(preCollect[0])
        misPreBLoc.append(preCollect[1])
    else:
        preBLoc.append('')
        misPreBLoc.append('')
    
    if type(dLine) is list and len(dLine) > 0:
        preCollect = collect(dLine[0], prefixDateRegex)
        preDLoc.append(preCollect[0])
        misPreDLoc.append(preCollect[1])
    else:  
        preDLoc.append('')
        misPreDLoc.append('')

postBLoc = []
misPostBLoc = []
postDLoc = []
misPostDLoc = []
for i in range(len(missedBirthLocation)):
    bLine = misPreBLoc[i]
    dLine = misPreDLoc[i]
    if type(bLine) is list and len(bLine) > 0:
        postCollect = collect(bLine[0], postfixDateRegex)
        postBLoc.append(postCollect[0])
        misPostBLoc.append(postCollect[1])
    else:
        postBLoc.append('')
        misPostBLoc.append('')
    
    if type(dLine) is list and len(dLine) > 0:
        postCollect = collect(dLine[0], postfixDateRegex)
        postDLoc.append(postCollect[0])
        misPostDLoc.append(postCollect[1])
    else:
        postDLoc.append('')
        misPostDLoc.append('')


'''
def scan(find, noFind):
    a = 0
    for i in missedLines:
        if len(i) > 0:
            if all([f in i[0] for f in find]) and all([not f in i[0] for f in noFind]):
                a += 1
    return a
'''







