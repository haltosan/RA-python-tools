'''
a - a-z
A - A-Z
z - a-zA-Z
. - any char
|12 - 1 or 2
+. - 1+
*. - 0+
?. - 0-1
'''


values = ['a','A','z','.']
functions = ['|','+','*','?']

def value(textChar, patternChar):
    if patternChar == 'a':
        return textChar in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    elif patternChar == 'A':
        return textChar in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    elif patternChar == 'z':
        return textChar in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    elif patternChar == '.':
        return True
    raise ValueError('Unknown pattern')

def tokenize(i, pattern):
    if i >= len(pattern):
        return '.'
    patternChar = pattern[i]
    if patternChar in values:
        return [patternChar, 1]
    elif patternChar in functions:
        if patternChar == '|':
            arg1 = tokenize(i + 1, pattern)
            arg2 = tokenize(i + 1 + arg1[-1], pattern)
            return [patternChar, arg1, arg2, 1 + arg1[-1] + arg2[-1]]
        else:
            arg1 = tokenize(i + 1, pattern)
            return [patternChar, arg1, 1 + arg1[-1]]
    raise ValueError('Unknown pattern')

def cmp(text,patternToken):
    patternToken = patternToken[0]  # strip off len
    if type(patternToken) is str:  # value
        if value(text[0], patternToken):
            return text[1:]
        return False
    else:  # function
        if patternToken[0] == '|':  # or
            cmp1 = cmp(text, patternToken[1])
            cmp2 = cmp(text, patternToken[2])
            if cmp1 != False:
                return cmp1
            elif cmp2 != False:
                return cmp2
            return False
        elif patternToken[0] == '+':  # 1 or more
            cmp1 = cmp(text, patternToken[1])
            if cmp1 != False:
                while len(text) > 0 and cmp1 != False:
                    text = text[1:]
                    cmp1 = cmp(text, patternToken[1])
                return text
            return False
        elif patternToken[0] == '*':  # 0 or more
            cmp1 = cmp(text, patternToken[1])
            while len(text) > 0 and cmp1 != False:
                text = text[1:]
                cmp1 = cmp(text, patternToken[1])
            return text
        elif patternToken[0] == '?':  # 0 or 1
            cmp1 = cmp(text, patternToken[1])
            if cmp1 != False:
                return cmp1
            return text
    raise ValueError('Unknown pattern')

def match(text, pattern):
    pass


