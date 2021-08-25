import re

### a predicate needs to take 1 string argument and return true or false
### these should be written to find specific characters or strings that need to be kept/removed
### set variables in the shell (p.SHORT_LEN = 10) instead of changing them here
###
### short/long use SHORT_LEN
### mostlyCaps uses MOSTLY_CAPS_THRESHOLD as the min percentage of caps to be true (inclusive)
### the regex function uses REGULAR_EXPRESSION, so be sure to set that before using the function

SHORT_LEN = 5
MOSTLY_CAPS_THRESHOLD = .75
REGULAR_EXPRESSION = r'^(?P<name>[A-Z][a-z]+, ([A-Z][a-z]+ ?)+).*'

def lower(text):
    return text.islower()
    
def upper(text):
    return text.isupper()
    
def blank(text):
    return len(text) == 0

def alpha(text):
    return text.isalpha()

def notAlpha(text):
    return not text.isalpha()

def alphaSpace(text):
    for char in text:
        if(char.isalpha() or char == ' '):
            pass
        else:
            return False
    return True

def alphaSpaceChar(text):
    return text.isalpha() or text == ' '

def upperWord(text):
    try:
        return text[0].isupper() and text[1:].islower()
    except IndexError:
        return False

def false(text):
    return False

def hasPage(text):
    return "PAGE" in text

def name(text):
    for char in text:
        if(char.isalpha() or char == ' ' or char == ','):
            pass
        else:
            return False
    return True

def nameChar(text):
    return text.isalpha() or text == ' ' or text == ','

def address(text):
    for char in text:
        if(char.isalpha() or char.isdigit() or char == ' ' or char == ',' or char == ','):
            pass
        else:
            return False
    return True

def addressChar(text):
    return text.isalpha() or text.isdigit() or text == ' ' or text == ',' or text == '.'

def short(text):
    return len(text) <= SHORT_LEN

def long(text):
    return not short(text)

def mostlyCaps(text):
    text = text.replace(' ','')
    if(len(text) == 0):
        return False
    score = 0
    for char in text:
        if(char.isupper()):
            score += 1
    return (score / len(text)) >= MOSTLY_CAPS_THRESHOLD

def indented(text):
    if(len(text) == 0):
        return False
    return text[0] == ' '

def regex(text):
    expression = re.compile(REGULAR_EXPRESSION)
    result = expression.search(text)
    return not result is None #result is None when re doesn't find anything
