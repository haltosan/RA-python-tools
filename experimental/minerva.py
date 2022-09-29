from file_analysis import *
pwd = r'C:\Users\esimmon1\Desktop\minerva'
os.chdir(pwd)

raw = get('exported.csv')
rawDates = csvColumn(raw, 1, True)[1:]  # remove column name

# there are several different dash characters used in the data; I tried to get most/all of them
# this takes care of the very common (date)-(date) format
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
def cacheSearch(i, lists, valid = lambda x: len(x) > 0 and len(x[0]) > 1):
    for lst in lists:
        n = lst[i]
        if valid(n):
            return n
    return None

# function to run a regex over both death and birth info and return the lists separately
def regexBirthDeath(regex, birthInfo, deathInfo, check = lambda x : type(x) is list and len(x) > 0):
    birthFound = []
    missBirth = []
    for line in birthInfo:
        if check(line):
            collection = collect(line[0], regex)
            birthFound.append(collection[0])
            missBirth.append(collection[1])
        else:
            birthFound.append('')
            missBirth.append('')
    deathFound = []
    missDeath = []
    for line in deathInfo:
        if check(line):
            collection = collect(line[0], regex)
            deathFound.append(collection[0])
            missDeath.append(collection[1])
        else:
            deathFound.append('')
            missDeath.append('')
    return birthFound, missBirth, deathFound, missDeath

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
            deathDates.append(deathCollection[0])
            missedDeathDates.append(deathCollection[1])
        else:
            birthDates.append('')
            missedBirthDates.append('')
            deathDates.append('')
            missedDeathDates.append('')

    # at this point, we have the dates for just about all lines (missed 3028 lines, 10%) 

    # the "'"+i[0][0] has ' to make sure excel doesn't mess with the data and [0][0] to extract just the string
    # the type and length check is to make sure we skip blank lines ([] or ' ')
    readableFormat = lambda lst : ["'"+i[0][0] if type(i) is list and len(i) > 0 else ' ' for i in lst]
    save(readableFormat(birthDates), 'bdates.csv', True)
    save(readableFormat(deathDates), 'ddates.csv', True)
    

def location():
    # now that we have the information split out, we can start pulling out location
    # the first easy case is "such and such was born January 1, 1987 in Townsville, SomeState"
    # the key here is the ' in '
    inRegex = r'.*? in (?P<location>.+)'

    # this creates one list each for birth and death, instead of several
    birthInfo = []
    deathInfo = []
    validCacheVal = lambda line : line is not None and type(line) is list
    for i in range(len(splitInfo)):
        line = cacheSearch(i, allInfo)
        if validCacheVal(line) and len(line[0]) >= 2:
            birthInfo.append([line[0][0]])
            deathInfo.append([line[0][1]])
        else:
            birthInfo.append('')
            deathInfo.append('')

    birthLocation, missedBirthLocation,deathLocation, missedDeathLocation = regexBirthDeath(inRegex,
                                                                                             birthInfo,
                                                                                             deathInfo,
                                                                                             validCacheVal)

    # capture all data that isn't a date and store them together
    notDateRegex = r'(?P<location1>.*?)((\d{1,2} ((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{4})|(((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{1,2},? \d{4})|(\d{4}))(?P<location2>.*)'
    notDatesB, misNotDatesB, notDatesD, misNotDatesD = regexBirthDeath(notDateRegex, missedBirthLocation, missedDeathLocation)

    # there are 2 capture classes we need to deal with now; quick processesing then next regex
    extractAndJoin = lambda lst: [[' '.join(i[0])] if (type(i) is list and len(i) > 0 and len(i[0]) == 2) else '' for i in lst]
    notDatesB = extractAndJoin(notDatesB)
    notDatesD = extractAndJoin(notDatesD)
    capsWordsRegex = r'.*?(?P<words>([A-Z][a-z]+..?)+).*'
    capsB, misCapsB, capsD, misCapsD = regexBirthDeath(capsWordsRegex, notDatesB, notDatesD)


    # we've gotten all the processing done that we can likely get done; it's time to format and save
    allInfoLoc = [birthLocation, capsB]
    allBLoc = []
    for i in range(len(birthLocation)):  # combine all the cache info into one list for each type
        line = cacheSearch(i, allInfoLoc, lambda x: type(x) is list and len(x) > 0)
        if line is not None:  # None is returned by cacheSearch if there's no info for that cell
                allBLoc.append(line)
        else:
                allBLoc.append([''])

    allInfoLoc = [deathLocation, capsD]
    allDLoc = []
    for i in range(len(birthLocation)):
        line = cacheSearch(i, allInfoLoc, lambda x: type(x) is list and len(x) > 0)
        if line is not None:
                allDLoc.append(line)
        else:
                allDLoc.append([''])

    def csvWrapper(text):  # a nice way to deal with all the formats in the final lists
        if type(text) is list:
                return '"'+' '.join(text)+'"'
        else:
                return csvText(text)

    save([csvWrapper(i) for i in [l[0] for l in allBLoc]], 'bloc.csv')  # saving the oddly formatted output
    save([csvWrapper(i) for i in [l[0] for l in allDLoc]], 'dloc.csv')


def prefixPostfix():  # this was a messy/failed attempt at getting the location data; didn't work out for several reasons
    prefixDateRegex = r'.*?(?P<location>([A-Z][A-Za-z]+? ?)+?).*?((\d{1,2} ((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{4})|(((Jan(uary)?)|(Feb(ruary)?)|(Mar(ch)?)|(Apr(il)?)|(May)|(Jun(e)?)|(Jul(y)?)|(Aug(ust)?)|(Sept(ember)?)|(Oct(ober)?)|(Nov(ember)?)|(Dec(ember)?)) \d{1,2},? \d{4})|(\d{4})).*'
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
    why this didn't work: the regex would capture the month names as a place name, ignore the rest of the date until the year
        ex: April 20, 1998  ->  location:'April' ignore:' 20, ' date:'1998'
            20 April 1998   ->  ignore:'20 ' location:'April' ignore:' ' date:'1998'
    the postfix regex still worked well, so I decided on just removing the date completely then looking for uppercased words both before and after the date
    '''








