from experimental import *
import signal
import time

pwd = r'C:\Users\esimmon1\Downloads\Massachusetts Institute of Technology\Massachusetts Institute of Technology'
os.chdir(pwd)

YEAR = r'(?P<year>(1(9(2|3).|\d\d\d|9.\d|.(2|3)\d))|(d(9\d\d|\d(2|3)\d))|(.9(2|3)\d)|(Sp\.)|(Grad\.))(?P<other>.*$)'
NUMERAL = r'(?P<numeral>[XVIxvil1]+)(?P<other>.*)'
NUMERAL_OLD = r'(?P<numeral>^.{1,2}[XVIxvil1]*)(?P<other>.*)'
LOCATION = r'^.* (?P<last>.*,.*)$'
NUMERAL_STRICT = r'(?P<num>^X?(|IX|IV|V?I{0,3})$)'



ree = r'19\d\d'
rules = [[r'\\d', '.']]

def findall(string, substr):
    return [m.start() for m in re.finditer(substr, string)]

def permute(string, rule):
    indices = findall(string, rule[0])
    for i in indices:
        pass  # slice and replace substr


 
def handler(signum, frame):
    global nextPsm
    res = input("Ctrl-c was pressed. Do you really want to stop this transcription? y/n ")
    if res == 'y':
        nextPsm = True
    if res == 'e':
        exit(0)
 
signal.signal(signal.SIGINT, handler)
 
count = 0
nextPsm = False
while True:
    print(count)
    count += 1
    time.sleep(0.1)
    if nextPsm:
        nextPsm = False
        count = 0
