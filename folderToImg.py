import os
import sys
from pdf2image import convert_from_path

IMAGE_QUALITY = 300
poppler_path = r'V:\FHSS-JoePriceResearch\papers\current\college_dataset\SAT_yearbooks\poppler-20.12.1\Library\bin'

def pdfToImages(pdfPath, imageFolder):
    """Convert each page of a pdf to an image and save to imageFolder"""
    try:
        os.mkdir(imageFolder)
    except:
        print(' Images in', imageFolder)
    # Image output naming convention: pageNum.png
    for pageNum in range(1, 200):
        print('  Imaging page', str(pageNum) + '...')
        try:
            page = convert_from_path(pdfPath, IMAGE_QUALITY, first_page = pageNum, last_page = pageNum, poppler_path = poppler_path, thread_count = 1)[0]
        except IndexError:  # when we try to convert a page that doesn't exist, we get this error on the [0] call
            break
        page.save(imageFolder + '\\' + str(pageNum) + '.' + 'PNG')


os.chdir(sys.argv[1])
outputDir = sys.argv[2]
nameList = [file for file in os.listdir() if file[-len('.PDF'):].upper() == '.PDF']
for name in nameList:
    pdfToImages(name, os.path.join(outputDir, name + '-images'))
