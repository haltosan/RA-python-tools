import os

def tess(args):
    os.system(r'cmd /k "V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\Tesseract-OCR\tesseract.exe ' + args + '"')


def oneWord():
    return '--psm 8'

def printOut():
    return 'stdout'

def tesseract(inSource, outSource, options=[]):
    args = []
    if inSource == 'terminal' or inSource == 'input':
        args.append('stdin')
    else:
        args.append('"'+inSource+'"')
    if outSource == 'print' or outSource == 'terminal':
        args.append(printOut())
    else:
        args.append('"'+outSource+'"')
    for option in options:
        args.append(option)
    tess(' '.join(args))
