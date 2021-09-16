from file_analysis import *

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
    catchThreshold = 2 #how many items from blacklist should appear in to remove
    moreCleanish = cleanFile(cleanish, lambda t: len([t for bad in blackList if bad in t]) > catchThreshold, negatePred = True)
    nlp = collect(moreCleanish, NAME + '(?P<info>.*)')
    save(nlp[0], 'pass 1' + fname + '.csv', True)
    save(nlp[1], 'check ' + fname + '.txt')
    
def mitGetManual(fname):
    x = ghostBuster(fname)
    save(x, 'manual ' + fname + '.txt')

