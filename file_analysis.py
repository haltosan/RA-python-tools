# -*- coding: utf-8 -*-
import os
import csv
import re
import predicates as p  # file of predicates for cleaning functions
#execfile(fName)
pwd = r'C:\Users\esimmon1\Downloads\Massachusetts Institute of Technology\Massachusetts Institute of Technology'
defaultRegex = r'^(?P<program>(M.?\d)|(T.?\d)|(Th.?\d)|(T-Th.?\d)|(G[^a-z])|(S[^a-z])|(U[^a-z]))'
PROGRAM = r'^(?P<program>(M.?\d)|(T.?\d)|(Th.?\d)|(T-Th.?\d)|(G[^a-z])|(S[^a-z])|(U[^a-z]))'
LOCATION = r'( |^)(?P<location>\d+ .*)'
FRAT = r'(?P<frat>((Alpha)|(Beta)|(Gamma)|(Delta)|(Epsilon)|(Zeta)|(Eta)|(Theta)|(Iota)|(Kappa)|(Lambda)|(Mu)|(Nu)|(' \
       r'Xi)|(Omicron)|(Pi)|(Rho)|(Sigma)|(Tau)|(Upsilon)|(Phi)|(Chi)|(Psi)|(Omega)).*) '
LOCATION2 = r'^((M.?\d)|(T.?\d)|(Th.?\d)|(T-Th.?\d)|(G[^a-z])|(S[^a-z])|(U[^a-z]))?(?P<location>.*)'
NAME = r'^(?P<name>[A-Z][A-Za-z]+,? ([A-Z](\.|[A-Za-z]+) ?){1,3}(, Jr)?)'

YEAR_RANGE = r'[23]'  # range of acceptable values in the 10's digit of the year
YEAR_WITH_ERRORS = r'(?P<year>(1(9'+YEAR_RANGE+r'.|\d\d\d|9.\d|.'+YEAR_RANGE+'\d))|(d(9\d\d|\d'+YEAR_RANGE+'\d))|(.9'+YEAR_RANGE+'\d))(?P<other>.*$)'
#this allows for 2 errors: the format should be 1 9 \YEAR_RANGE\ digit; any digit (other than expected) in the first 3 chars counts as 1 error, a wildcard character anywhere counts as 2 errors

################################################################################
# chk - check file, texts - some list of text
# text - string, outl - outList, outs - outString
# most everything is the texts of a file except in merge (takes file names)
#
# GENERAL: init(), get(fileName, splt='\n'), save(text, out, csv=False)
# find(item, texts)
#
# CHECK FILES: calcScores(raw, check), findLarge(n, scores),
# getSame(chk,other, rems=[' ',',','"']) getContext(chk,other, rems=[' ',',','"'])
# merge(inName, contextName, regex=defaultRegex)
#
# CSV: csvJoin(texts), csvSplit(text), csvText(text), csvColumn(texts, n)
# csvMergeColumn(fullTexts, column, n)
#
# CLEAN: clean(text,rems=[' ',',','"'], negate = False)
# cleanFile(texts, pred = None, cleaner = clean, cleanerArg = ['\t','\ufeff'], negatePred = False, negateClean = False)
# cleanWords(text, pred, negate = False), cleanChars(text, pred, negate = False)
# cleanColumn(texts, n, cleaner = cleanChars, cleanerArg = p.nameChar)
# charStrip(texts, chars, negate = False)
#
# COLLECT: collect(text, regex=defaultRegex)
#
# MISC: headerGrab(texts, headerPred, quite = True), infoGrab(fname, outName)
# slapThatInfoOn(texts)
#
#
################################################################################


#########################
### GENERAL FUNCTIONS ###
#########################

def init():
    """Gets shell in correct dir and runs any other init stuff you need"""
    os.chdir(pwd)


def get(fileName, splt='\n'):
    """returns file fileName as a list split on the splt string"""
    x = open(fileName, 'r', encoding='utf-8')
    lines = x.read().split(splt)
    x.close()
    return lines


def save(text, out, csvStyle=False):
    """writes text to out (file name), can do it in a csv format"""
    x = open(out, 'w', encoding='utf-8')
    if type(text) is str:
        if ',' in text:
            text = '"' + text + '"'
        x.write(text)
    elif type(text) is list:
        if type(text[0]) is list:  # nested lists
            outl = []
            if csvStyle:
                for i in text:
                    outl.append(csvJoin(i))
            else:
                for i in text:
                    outl.append(' '.join(i))
            x.write('\n'.join(outl))
        else:  # just a normal list
            if csvStyle:
                outl = list()
                for i in text:
                    outl.append(csvText(i))
                x.write('\n'.join(outl))
            else:
                x.write('\n'.join(text))  # puts \n between cells
    else:
        x.close()
        raise Exception("Unknown type, don't be a dummy")
    x.close()


def find(item, texts):
    """finds item in texts if they're sort of similar"""
    for i in range(len(texts)):
        txt = clean(texts[i])  # [:first])
        if len(txt) == 0:
            continue
        elif txt in clean(item) or clean(item) in txt:
            return i
    return None


############################
### CHECK FILE FUNCTIONS ###
############################

def calcScores(raw, check):
    """records errors per page"""
    scores = []
    for pg in raw:
        score = 0
        for ln in check:
            if ln in pg:
                score += 1
        scores.append(score)
    return scores


def findLarge(n, scores):
    """print the index of anything larger than n"""
    for i in range(len(scores)):
        if scores[i] >= n:
            print(i)


def getSame(chk, other, rems=[' ', ',', '"']):
    """finds all lines that are the same in two files w/out duplicates"""
    same = set()
    for lc in chk:
        for lo in other:
            if clean(lc, rems) == clean(lo, rems):
                same.add(lc)
                break
    return same


def getContext(chk, other, rems=[' ', ',', '"']):
    """finds where lines from a check file belong in the raw input file\
creates context (line before, check line, line after, \n) for merge function"""  # used for merge
    outs = ""
    for lc in chk:
        for i in range(len(other)):
            if clean(lc, rems) == clean(other[i], rems):
                outs += (other[i - 1 if i - 1 > 0 else 0]) + '\n'
                outs += (other[i]) + '\n'
                outs += (other[i + 1 if i < len(other) else len(other) - 1]) + '\n\n'
                break
    return outs


def merge(inName, contextName, regex=defaultRegex):
    """places info from check file in proper place and returns collect-ed text with a check list"""
    conRaw = get(contextName, '\n\n')
    inn = get(inName)
    con = []
    for i in conRaw:
        con.append(i.split('\n'))

    del inn[-1]
    check = []
    for block in con:
        if len(block) <= 1:
            continue
        if len(block[0]) == 0:
            del block[0]
        nlp = collect(block[1], regex=regex)  # 1=middle; others are used to search up the line
        if len(nlp[0]) == 0:
            check.append(nlp[1])
            continue
        text = nlp[0][0]  # gets list from nested list
        i = find(block[0], inn)
        if i is not None:
            context = csvSplit(inn[i])
            if len(context) != 8:
                context = csvSplit(inn[i + 1])
            if len(context) != 8:  # not enough info to generate line
                check.append(nlp[0])
            else:
                newLine = text
                newLine.insert(1, context[1])  # school
                newLine.insert(2, context[2])  # standing
                # newLine.insert(4,'')
                newLine = newLine + [context[5]]  # year
                newLine = newLine + ['University of Pennsylvania', 'Pennsylvania', '1']
                inn.insert(i + 1, csvJoin(clean(newLine, ['"'])))
                print(i + 1, ','.join(newLine))

        else:
            i = find(block[2], inn)
            if i is not None:
                context = csvSplit(inn[i])
                if len(context) != 8:
                    context = csvSplit(inn[i - 1])
                if len(context) != 8:
                    check.append(nlp[0])
                else:
                    newLine = text
                    newLine.insert(1, context[1])  # school
                    newLine.insert(2, context[2])  # standing
                    # newLine.insert(4,'')
                    newLine = newLine + [context[5]]  # year
                    newLine = newLine + ['University of Pennsylvania', 'Pennsylvania', '1']
                    inn.insert(i - 1, csvJoin(clean(newLine, ['"'])))
                    print(i - 1, ','.join(newLine))
            else:
                check.append(nlp[0])
    return inn, check


#####################
### CSV FUNCTIONS ###
#####################

### I know there's most likely already a library for this, but I wrote my own stuff

def csvJoin(texts):
    """converts list to csv string"""
    outs = ""
    for i in texts:
        if ',' in i:
            i = '"' + str(i) + '"'
        outs += str(i) + ','
    return outs.strip(',')


def csvSplit(text):
    """converts csv string to list"""
    texts = []
    curString = ""
    inString = False
    for char in text:
        if char == '"':
            inString = not inString
        if char == ',' and not inString:
            texts.append(curString)
            curString = ""
        elif char != '"':  # TODO: figure out how to remove only the quotes that escape stuff, not literal quotes
            curString += str(char)
    texts.append(curString)
    return texts


def csvText(text):
    """turns text into proper csv string"""
    return '"' + text + '"' if (',' in text) else text


def csvColumn(texts, n, safe=True):
    """get a column from a csv file"""
    outl = list()
    for i in texts:
        try:
            outl.append(clean(csvSplit(i)[n], ['"']))
        except IndexError:
            if safe:
                outl.append([])
            else:
                raise IndexError("Index " + str(n) + " out of range for texts")
    return outl


def csvMergeColumn(fullTexts, column, n):
    """given a csv file, replace a column with the corresponding item from 'column' list"""
    outl = list()
    for i in range(len(fullTexts)):
        outl.append(csvSplit(fullTexts[i])[:n] + [column[i]] + csvSplit(fullTexts[i])[n + 1:])
    return outl


#######################
### CLEAN FUNCTIONS ###
#######################

### clean functions need 3 arguments: text(s), arg, negate
### negate needs to be named negate, but it isn't positional
### the argument is normally a predicate, but it doesn't have to be
### clean functions are expected to return text(s)

def clean(text, rems=None, negate=False):  # negate not implemented
    """removes rems text from text/texts"""
    if rems is None:
        rems = [' ', ',', '"']
    if type(text) is str:
        for r in rems:
            text = text.replace(r, '')
    elif type(text) is list:
        out = list()
        for i in text:
            line = i
            for r in rems:
                line = line.replace(r, '')
            out.append(line)
        text = out
    return text


def cleanFile(texts, pred=None, cleaner=None, cleanerArg=None, negatePred=False, negateClean=False):
    """pred (remove line if false), cleaner (run on each line), cleanerArg (argument for cleaner), can negate pred/clean"""
    if cleanerArg is None:
        cleanerArg = ['\t', '\ufeff']
    outl = []
    for line in texts:
        if (pred is not None) and (pred(line) if negatePred else not pred(line)):  # short circut to prevent None(line); skip if pred is not true
            pass
        else:
            if cleaner is None:
                outl.append(line)
            else:
                outl.append(cleaner(line, cleanerArg, negate=negateClean))
    return outl


def cleanWords(text, pred, negate=False):
    """skip words that cause pred to be false, can negate predicate"""
    words = text.split(' ')
    outl = []
    for word in words:
        if pred(word) if negate else not pred(word):  # skip if pred is false, or opposite if negate is true
            pass
        else:
            outl.append(word)
    return ' '.join(outl)


def cleanChars(text, pred, negate=False):
    """skip chars that cause pred to be false, can negate predicate"""
    outs = ""
    for char in text:
        if pred(char) if negate else not pred(char):  # skip if pred is false, or opposite if negate is true
            pass
        else:
            outs += char
    return outs


def cleanColumn(texts, n, cleaner=cleanChars, cleanerArg=p.nameChar):
    """run a cleaner file on a column of a csv file"""
    col = csvColumn(texts, n)
    cleanCol = cleanFile(col, cleaner=cleaner, cleanerArg=cleanerArg)
    return csvMergeColumn(texts, cleanCol, n)


def charStrip(texts, chars, negate=False):  # negate not implemented; only for compatibility
    """removes chars from tails of texts (like trailing spaces)"""
    if type(texts) is str:
        for i in range(len(chars)):  # almost worst case has chars list in reverse on the end
            for char in chars:
                texts = texts.strip(char)
    elif type(texts) is list:
        outl = texts
        for i in range(len(chars)):
            for line in range(len(texts)):
                for char in chars:
                    outl[line] = outl[line].strip(char)
        texts = outl
    else:
        raise Exception("Unknown type for texts arg")
    return texts


def borderBlocks(i, f):
    blockSize = 5
    offset = int(blockSize * .3)
    b1 = [clean(i, ' "')[0] for i in f[i - offset - blockSize : i - offset]]
    b2 = [clean(i, ' "')[0] for i in f[i + blockSize - offset : i + 2 * blockSize - offset]]
    getTrump = lambda lst : max(set(lst), key=lst.count)
    t1 = getTrump(b1)
    t2 = getTrump(b2)
    alpha = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    try:
        trumpDiff = (alpha.index(t2) - alpha.index(t1))
    except ValueError:
        print(t1, t2, f[i])
        return False  # trump not in alphabet
    if trumpDiff <= 2 and trumpDiff >= 0:        
        firstValue = ord(clean(f[i], ' "')[0])
        if firstValue >= ord(t1) and firstValue <= ord(t2):
            return True
    print(t1, t2, f[i])
    return False


def ghostBuster(fname):  # finds lines that start with a strange letter (b in the middle of the e section)
    f = get(fname)
    blockSize = 20
    outl = []
    for block in range(int(len(f) / blockSize)):
        letters = [clean(i, ' "')[0] for i in f[block * blockSize : block * blockSize + blockSize]]  # first letters of lines in block
        trump = max(set(letters), key = letters.count)  # most common starting letter
        for i in range(blockSize):
            lnIndex = block * blockSize + i
            line = f[lnIndex]
            if clean(line, ' "')[0] != trump:
                if (i <= int(blockSize*.3) or i>= blockSize - int(blockSize*.3)):
                    if borderBlocks(lnIndex, f):
                        pass
                    else:
                        outl.append(line)
                else:
                    outl.append(line)  # anomaly
    return outl


###############
### COLLECT ###
###############

def collect(text, regex=defaultRegex, spaceMatches=False):  # basically the same as the nlp.py project, just accepts lists now
    """returns everything that matches the regex in matches, leftovers in non_matches"""
    people_re = re.compile(regex)
    matches = []
    non_matches = []
    if type(text) is list:
        for line in text:
            i = people_re.search(line)
            if i is not None:
                # matches.append((i.groupdict()['first'].strip() + ' ' + i.groupdict()['last'].strip(), i.groupdict()['info']))
                matches.append(list(i.groupdict().values()))
                # matches.append([i.goupdict()['info1'], i.groupdict()['name'], i.groupdict()['info']])
            else:
                if spaceMatches == 'keep':
                    matches.append(line)
                elif spaceMatches == True:
                    matches.append('')  # if a line doesn't match the regex, put a blank line
                non_matches.append(line)
        return matches, non_matches
    # This loop looks through lines (from above) and appends each match to a list, formatted the way we want
    elif type(text) is str:
        for line in text.split('\n'):
            i = people_re.search(line)
            if i is not None:
                # matches.append((i.groupdict()['first'].strip() + ' ' + i.groupdict()['last'].strip(), i.groupdict()['info']))
                # matches.append([i.groupdict()['name'],i.groupdict()['addressPt1'],i.groupdict()['addressPt2']])
                matches.append(list(i.groupdict().values()))
            else:
                non_matches.append(line)
        return matches, non_matches
    else:
        return Exception("Unknown text argument type")


######################
### MISC FUNCTIONS ###
######################


def headerGrab(texts, headerPred, quite=True):
    """finds headers and attaches that as info to names following, until next header)"""
    # example: SENIORS \n Joe Smith \n Frank Stevenson
    # gives us:
    # [Joe Smith, SENIORS],
    # [Frank Stevenson, SENIORS]
    file = texts
    info = 'NONE'
    outl = []
    for i in range(len(file)):
        if headerPred(file[i]):
            if not quite:
                print(file[i])
                print(":next:", file[i + 1])
                # y - info+= line
                # n - not header, skip
                # r - refresh/clear info
                # anything else - info += input
                maybeInfo = input('y/n/r/info: ')
                if maybeInfo == 'r':
                    info = ''
                    maybeInfo = input('y/n/info: ')
                if maybeInfo == 'n':
                    pass
                elif maybeInfo == 'y':
                    info += ' ' + file[i]
                else:
                    info += ' ' + maybeInfo
            else:
                info = file[i]
        else:
            outl.append([file[i], info])
    return outl


def infoGrab(fname, outName):
    """pulls info off of names (John Smith, English) and moves it over a column"""
    f = get(fname)
    if len(f[-1]) < 1:
        del f[-1]
    names = csvColumn(f, 0)
    info = csvColumn(f, 1)
    for i in range(len(names)):
        if ',' in names[i]:
            cIndex = names[i].index(',')
            if 'Jr' in names[i][cIndex:] or 'JR' in names[i][cIndex:]:
                pass
            else:
                info[i] = names[i][cIndex:] + ', ' + info[i]
                names[i] = names[i][:cIndex]
    o1 = csvMergeColumn(f, names, 0)
    save(o1, 'tmp.txt')
    o2 = get('tmp.txt')
    o3 = csvMergeColumn(o2, info, 1)
    save(o3, outName)


def slapThatInfoOn(texts):
    """attaches info on lines after names (John Smith \\n Science \\n 1922)\
\nneed to set p.REGULAR_EXPRESSION to identify names"""
    outl = []
    nameInfo = []
    for line in texts:
        if p.regex(line):
            outl.append(nameInfo)
            nameInfo = [line]
        else:
            nameInfo.append(line)

    return outl


################################################################################
##################################### RUN ######################################
################################################################################

init()
print(pwd)


################################################################################
################################################################################
################################################################################

