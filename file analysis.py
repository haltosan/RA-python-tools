# -*- coding: utf-8 -*-
import os
import csv
import re
import predicates as p  # file of predicates for cleaning functions
#execfile(fName)
pwd = r'C:\Users\haltosan\OneDrive\Desktop\nlp\Massachusetts Institute of Technology\Massachusetts Institute of Technology'
defaultRegex = r'^(?P<program>(M.?\d)|(T.?\d)|(Th.?\d)|(T-Th.?\d)|(G[^a-z])|(S[^a-z])|(U[^a-z]))'
PROGRAM = r'^(?P<program>(M.?\d)|(T.?\d)|(Th.?\d)|(T-Th.?\d)|(G[^a-z])|(S[^a-z])|(U[^a-z]))'
LOCATION = r'( |^)(?P<location>\d+ .*)'
FRAT = r'(?P<frat>((Alpha)|(Beta)|(Gamma)|(Delta)|(Epsilon)|(Zeta)|(Eta)|(Theta)|(Iota)|(Kappa)|(Lambda)|(Mu)|(Nu)|(' \
       r'Xi)|(Omicron)|(Pi)|(Rho)|(Sigma)|(Tau)|(Upsilon)|(Phi)|(Chi)|(Psi)|(Omega)).*) '
LOCATION2 = r'^((M.?\d)|(T.?\d)|(Th.?\d)|(T-Th.?\d)|(G[^a-z])|(S[^a-z])|(U[^a-z]))?(?P<location>.*)'
NAME = r'^(?P<name>[A-Z][A-Za-z]+,? ([A-Z](\.|[A-Za-z]+) ?){1,3}(, Jr)?)'


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
        else:
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

###########################################
### MOST LIKELY NOT REUSABLE
###########################################

def nameCleanInfo(f, n):
    o1 = slapThatInfoOn(f)
    names = []
    for i in o1:
        names.append(i[0])
    names[0] = clean(names[0], ['\ufeff'])
    save(names, 'names' + str(n) + '.txt')
    reee = "(?P<name>[A-Z][a-z]+, ((([A-Z][A-Za-z]+.?)+)))"
    nolineNames = '\n'.join(names)
    nlp = collect(nolineNames, reee)
    outs = ''
    outl = []
    for i in nlp[0]:
        for l in i:
            outs += l
        outl.append(outs)
        outs = ''
    save(names, 'names' + str(n) + '.txt')
    cleanNames = outl
    full = o1
    noname = o1
    for i in range(len(names)):
        noname[i][0] = noname[i][0].replace(names[i], '')
    info = []
    for i in noname:
        info.append(' '.join(i))

    nameInfo = []
    for i in range(len(info)):
        nameInfo.append([cleanNames[i], clean(info[i], [',', '"', '\''])])
    save(nameInfo, '192' + str(n) + ' need info clean.csv')


def geoff(f, n):
    reee = "(?P<name>[A-Z][a-z]+, [A-Z][a-z]+(,? )([A-Z][a-z]+)?(jr.)?), "
    names = []
    # f = clean(f, ['\ufeff','\uffff','\''])
    f[0] = clean(f[0], ['\ufeff'])
    for i in f:
        names.append(collect(i, reee)[0])
    outs = ''
    tmp = []
    for i in names:
        for l in i:
            outs += ' '.join(l)
        tmp.append(outs)
        outs = ''
    names = tmp
    outl = []
    for i in range(len(f)):
        line = f[i]
        n1 = names[2 * i]
        n2 = names[2 * i + 1]
        if len(n1) < 0:
            line = line.replace(n1, '\uffff')
        if len(n2) < 0:
            line = line.replace(n2, '\uffff')
        outl.append(line)


def tim(f):
    ree = r'(?P<name>[A-Z][a-z]+(,? )[A-Z][a-z]+(,? )([A-Z][a-z]+)?(jr.)?)(?P<info1>(, )?\d*([A-Za-z\. ]*), [A-Za-z, ]+[^\.]*\. [A-Z\. ]*)(?P<name2>[A-Z][a-z]+(,? )[A-Z][a-z]+(,? )([A-Z][a-z]+)?(jr.)?)(?P<info2>(, )?.*)'
    reee = r"(?P<name>[A-Z][a-z]+(,? )[A-Z][a-z]+(,? )([A-Z][a-z]+)?(jr.)?)(, )?\d*([A-Za-z\. ]*), [A-Za-z, ]+[^\.]*\. [A-Z\. ]*(?P<name2>[A-Z][a-z]+(,? )[A-Z][a-z]+(,? )([A-Z][a-z]+)?(jr.)?)(, )?.*"
    names = []
    p.SHORT_LEN = 21
    f = cleanFile(f, p.long, cleanerArg=['‘', '\ufeff', '\t', '*', '"', '|', '-', '!', '“', '_', '’', '—', '\'', ';',
                                         'CATALOGUE OF STUDENTS', 'CORNELL UNIVERSITY REGISTER', '”', '/', '¢', '»'])
    f = cleanFile(f, cleaner=cleanChars, cleanerArg=p.addressChar)
    # f = cleanFile(f, pp)
    nlp = collect(f, ree)
    return nlp


def george():
    raw = get('1924.txt')
    names = get('set names2.txt')
    ninfo = []
    for line in raw:
        for i in range(len(names)):
            if names[i] in line:
                ninfo.append([names[i], line.replace(names[i], '!')])
                names[i] = '\ueeee'
                break
    return ninfo, names


def getCol(texts, n):
    outl = []
    for i in texts:
        outl.append(i[n])
    return outl


def mergeCol(texts, col, n):
    outl = texts.copy()
    for i in range(len(texts)):
        outl[i][n] = col[i]
    return outl.copy()


def sandra():
    b = george()
    ninfo = b[0]
    names = b[1]
    p.SHORT_LEN = 3
    cleanNames = cleanFile(names, p.long, cleaner=None)
    save(cleanNames, 'leftover names.txt')
    col1 = getCol(ninfo, 0)
    col2 = getCol(ninfo, 1)
    col3 = [None] * len(col2)
    for i in range(len(col2)):
        for l in range(len(cleanNames)):
            name = cleanNames[l]
            if name in col2[i]:
                col3[i] = name
                col2[i] = col2[i].replace(name, '@')
                cleanNames[i] = '\ueeee'
                break
    f = [[None, None, None]] * len(col1)
    f = mergeCol(f, col1, 0)
    f = mergeCol(f, col2, 1)
    f = mergeCol(f, col3, 2)
    return f, col3


keep = []


def monica():
    global keep
    r1 = r'((A|AChem|Ag|Ar|L|C|M|E|Eng|MD|V|Grad|Sp).*)?(?P<name>'
    r2 = r'([A-Za-z ]+,){2}( jr.)?)(?P<info>.*)$'
    char = 'A'
    chk = []
    keep = []
    reee = ''
    f = get('info.txt')
    for i in range(ord('A'), ord('Z') + 1):
        char = chr(i)
        reee = r1 + char + r2
        nlp = collect(f, reee)
        keep.append(nlp[0])
        chk.append(nlp[1])
        f = nlp[1]

    return keep, chk


info = []


def rita():
    # col2[i] may be nlp[0] if we get anything, else nlp[1]
    global keep, chk, info
    keep = []
    chk = []
    raw = get('names.csv')
    info = csvColumn(raw, 1)
    r1 = r'((A|AChem|Ag|Ar|L|C|M|E|Eng|MD|V|Grad|Sp).*)?(?P<name>'
    r2 = r'([A-Za-z ]+,){2}( jr.)?)(?P<info>.*)$'
    char = 'A'
    reee = ''
    for letterIndex in range(ord('A'), ord('Z') + 1):
        char = chr(letterIndex)
        reee = r1 + char + r2
        for i in range(len(info)):
            nlp = collect(info[i], reee)
            if len(nlp[0]) > 0:
                info[i] = nlp[0][0]  # set equal to info w/out 2nd name


def megan():
    f = get('info.txt', '\n\n')
    info = []
    for i in f:
        info.append(i.split('\n'))
    outl = []
    i = 0
    r1 = r'(?P<info1>((A|AChem|Ag|Ar|L|C|M|E|Eng|MD|V|Grad|Sp).*)?)(?P<name>'
    r2 = r'([A-Za-z ]+,){2}( jr.)?)(?P<info>.*)$'
    for letterIndex in range(ord('A'), ord('Z') + 1):
        char = chr(letterIndex)
        reee = r1 + char + r2
        for line in info[i]:
            nlp = collect(line, reee)
            outl.append(nlp)
        i += 1
    o1 = []
    for i in outl:
        o1.append(list(i))
    o2 = []
    for i in o1:
        if len(i[0]) == 1:
            o2.append([i[0][0], i[1]])
        else:
            o2.append([i[0], i[1]])
    o3 = []
    for i in o2:
        s = []
        if len(i[0]) < 1:
            s.append(' ')
        else:
            s.append(i[0][0])
        if len(i[1]) < 1:
            s.append(' ')
        else:
            s.append(i[1][0])
        o3.append(s)
    o4 = []
    for i in o2:
        o4.append([i[1], i[0]])
    o5 = []
    for i in o4:
        s = [i[0][0] if (len(i[0]) > 0) else ' ']
        if len(i[1]) < 1:
            s.append(' ')
        else:
            for l in i[1]:
                s.append(l if (len(l) > 0) else ' ')
        o5.append(s)
    return o5


def john(fname='1922 need info clean.csv'):
    f = get(fname)
    reee = r'^.*(?P<year>19\d{2}).*$'
    ree = r'^.*(?P<year>2\d).*$'
    info = csvColumn(f, 1)
    for i in range(len(info)):
        if len(info[i]) < 1:
            info[i] = ' '
    o1 = []
    for i in info:
        nlp = collect(i, ree)
        o1.append(nlp[0])
    o2 = []
    for i in o1:
        if len(i) < 1:
            o2.append(' ')  # empty
        else:
            o2.append('19' + i[0][0])
    return o2


def joan(fname='1922 need info clean.csv'):
    f = get(fname)
    reee = r'^.*(1\d{3}) ?(?P<program>(A \(Chem\))|(Ag)|(Ar)|(FA)|(Grad)|(Sp)|(A)|(C)|(M)|(E)|(V))'
    ree = r'\d(?P<program>(AChem)|(Ag)|(Ar)|(FA)|(Grad)|(Sp)|(MD)|(A)|(C)|(M)|(E)|(V))'
    info = csvColumn(f, 1)
    for i in range(len(info)):
        if len(info[i]) < 1:
            info[i] = ' '
    o1 = []
    for i in info:
        nlp = collect(i, ree)
        if len(nlp[0]) < 1:
            o1.append(' ')
        else:
            o1.append(nlp[0][0][0])
    o2 = []
    programs = {'A': 'Arts and Sciences', 'AChem': 'Arts and Sciences, Department of Chemistry',
                'Ag': 'Agriculture', 'Ar': 'Architecture', 'L': 'Law', 'Eng': 'Enginerring', 'FA': 'Fine Arts',
                'C': 'Civil Engineering', 'M': 'Mechanical Engineering', 'E': 'Electrical Engineering', ' ': '',
                'MD': 'Medical College', 'V': 'Veterinary College', 'Grad': 'Graduate School', 'Sp': 'Special Student'}
    for i in o1:
        o2.append(programs[i])
    o3 = []
    for i in o2:
        o3.append(csvText(i))
    return o3


def jeffery(fname='1924 need info clean.csv'):
    f = get(fname)
    reee = r'\d((AChem)|(Ag)|(Ar)|(FA)|(Grad)|(Sp)|(MD)|(A)|(C)|(M)|(E)|(V))(?P<location>.*)'
    info = csvColumn(f, 1)
    for i in range(len(info)):
        if len(info[i]) < 1:
            info[i] = ' '
    o1 = []
    for i in info:
        nlp = collect(i, reee)
        if len(nlp[0]) < 1:
            o1.append(' ')
        else:
            o1.append(nlp[0][0][0])
    o2 = []
    for i in o1:
        o2.append(csvText(i))
    return o2


def fileStrip(f, cleanerArg=',. '):
    # assume a header
    outl = []
    i = 0
    while True:
        try:
            column = csvColumn(f, i)  # throws out of bounds error when index is wrong
            i += 1
        except IndexError:
            return outl
        newCol = cleanFile(column, cleaner=charStrip, cleanerArg=cleanerArg)
        outl.append(newCol)


def ghostBuster(fname='Cornell 1920s NLP Output.csv'):  # finds lines that start with a strange letter (b in the middle of the e section)
    f = get(fname)
    blockSize = 20
    outl = []
    for block in range(int(len(f) / blockSize)):
        letters = []
        scores = []
        for i in range(blockSize):
            line = clean(f[block * blockSize + i], '" ')
            letters.append(line[0])
            scores.append(0)
        for i in range(len(letters)):
            for l in letters:
                if l == letters[i]:
                    scores[i] += 1
        trump = letters[scores.index(max(scores))]  # most common letter in this section
        for i in range(blockSize):
            line = f[block * blockSize + i]
            if clean(line, '"')[0] != trump:
                outl.append(line)
            else:
                pass
                #outl.append(line)
    return outl


def settingsChanger():
    configPath = r'config.txt'
    config = get(configPath)
    quality = int(config[5])
    maxNames = -1
    last = -1
    current = 0
    change = 75
    up = True
    regex = r'^(?P<name>A[a-z]+, ([A-Z][a-z]+(, )?)+)'
    while input('[]') != 'end':
        f = get('Cornell_1921-12.txt')
        nlp = collect(f, regex)
        current = len(nlp[0])
        if current < last - 3:
            up = not up
            change /= 2
        if current > maxNames:
            print('max:', current, quality)
            maxNames = current
        print(current, quality)
        last = current
        quality += (1 if up else -1) * change
        quality = int(quality)
        config[5] = str(quality)
        save(config, configPath)
        save(nlp[0], 'tmp.txt')


def bestPages(dirname='52'):
    outll = []
    os.chdir(dirname)
    dirScan = os.scandir()
    formats = []
    numNamesFound = [0] * 5  # 5 file formats
    regex = NAME
    while True:
        try:
            fname = next(dirScan).name
        except StopIteration:
            break
        f = get(fname, 'PAGE')
        formats.append(f)
    del dirScan, dirname, f, fname
    nameSum = 0
    chosens = []
    for pageI in range(2):
        for fIndex in range(len(formats)):
            f = formats[fIndex]
            page = f[pageI].split('\n')
            nlp = collect(page, regex)
            numNamesFound[fIndex] = len(nlp[0])
        chosenOne = numNamesFound.index(max(numNamesFound))
        chosens.append(chosenOne)
        nameSum += numNamesFound[chosenOne]
        outll.append(collect(formats[chosenOne][pageI], regex))

    print(nameSum, "total names")
    settings = [1, 12, 3, 4, 6]
    print('Best setting:', settings[max(set(chosens), key=chosens.count)])
    os.chdir('..')
    return outll


def cleanCollect(fname='4.txt'):
    f = get(fname)
    o1 = cleanFile(f, p.space, negatePred=True)
    o2 = cleanFile(o1, p.hasPage, negatePred=True)
    p.SHORT_LEN = 10
    o3 = cleanFile(o2, p.long)
    save(o3, fname + ' clean.txt')
    f = get(fname + ' clean.txt')
    nlp = collect(f)
    save(nlp[0], 'nlp.csv', csvStyle=True)
    save(nlp[1], 'check.txt')


def infoExtract(fname, infoN=2, regex=defaultRegex, outCol=4, spaceMatches=True):
    f = get(fname)
    for i in range(len(f)):
        while len(csvSplit(f[i])) < outCol:
            f[i] += ', '  # make sure we have the right amount of cols
    info = csvColumn(f, infoN)
    for i in range(len(info)):
        if len(info[i]) < 1:
            info[i] = ' '  # collect no like blank strings
    nlp = collect(info, regex=regex, spaceMatches=spaceMatches)
    infol = []
    for i in nlp[0]:
        if type(i) is list:
            infol.append(i[0])  # remove nested lists
        else:
            infol.append(i)
    o1 = csvMergeColumn(f, infol, outCol)
    for i in range(len(o1)):
        if len(o1[i]) < outCol:
            o1[i].append(' ')  # i think this makes the blank cells into spaces
    outl = []
    for i in o1:
        s = []
        for col in i:
            s.append(clean(col, '"'))
        outl.append(s)
    return outl

def foil(dirname = '52'):
    os.chdir(dirname)
    f = get('Columbia_19'+dirname+'-1.txt')
    o1 = cleanFile(f, pred = p.hasPage, negatePred = True)
    o2 = cleanFile(o1, pred = p.long)
    o3 = cleanFile(o2, pred = lambda t : t[:4] == 'With' or t[:2] == 'in' or t[:4] == 'High' or 'Honors' in t, negatePred = True)
    save(o3, 'cleaner.txt')
    os.chdir('..')

def mitPass1(fname):
    f = get(fname)
    cleanish = cleanFile(cleanFile(f, p.long), p.hasPage, negatePred=True)
    blackList = ['Name', 'Class', 'Course', 'Home']
    catchThreshold = 2
    moreCleanish = cleanFile(cleanish, lambda t: len([t for bad in blackList if bad in t]) > catchThreshold, negatePred = True)
    nlp = collect(moreCleanish, NAME + '(?P<info>.*)')
    save(nlp[0], 'pass 1' + fname + '.csv', True)
    save(nlp[1], 'check ' + fname + '.txt')
    
