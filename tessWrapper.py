import os

TESSERACT_PATH = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\Tesseract-OCR\tesseract.exe'

def tess(args):
    os.system(r'cmd /k "' + TESSERACT_PATH + ' ' + args + '"')


def oneWord():
    return '--psm 8'

def tesseract(inSource, outSource, options=[]):
    args = []
    if inSource == 'terminal' or inSource == 'input':
        args.append('stdin')
    else:
        args.append('"'+inSource+'"')
    if outSource == 'print' or outSource == 'terminal':
        args.append('stdout')
    else:
        args.append('"'+outSource+'"')
    if type(options) is list:
        for option in options:
            args.append(option)
    elif type(options) is str:
        args.append(option)
    tess(' '.join(args))
