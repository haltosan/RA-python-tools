"""
Authors: Ethan, Annie, Sarah
Requires the record_linking environment to work properly (very specific dectron2, pywin32, etc. versions)
"""

import pytesseract
import cv2
import layoutparser as lp
import shutil
import os
import sys
import random
from re import findall
try:
 from PIL import Image
except ImportError:
 import Image

from pdf2image import convert_from_path

# misc settins; no major need to change for the most part
DEBUG = True
PDF_2_IMAGE_THREADS = 1
IMAGE_FILE_TYPE = 'PNG'  # make sure this is uppercase
IMAGE_QUALITY = 300

# command line flags
delImages = False
useCache = False
imageOnly = False

# all based on getSettings()
workingDir = ''
imageFolder = ''
textLabel = ''
pdfPath = ''
imagePath = ''
outTextPath = ''

# params for layoutParser model creation
config_path = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\layoutParser\primaLayout\config.yaml'
model_path = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\layoutParser\primaLayout\model_final.pth'
# params for pdf2image
poppler_path = r'V:\FHSS-JoePriceResearch\papers\current\SAT_yearbooks\poppler-20.12.1\Library\bin'
startPage, endPage = 0,0
# tesseract path
pytesseract.pytesseract.tesseract_cmd = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\Tesseract-OCR\tesseract.exe'


######################
## HELPER FUNCTIONS ##
######################


def dPrint(txt):
    """Print debugging info"""
    if DEBUG:
        print('*' + str(txt) + '*')


def csvText(text):
    """turns text into proper csv string"""
    return '"' + text + '"' if (',' in text) else text


def csvJoin(texts):
    """converts list to csv string"""
    outs = ""
    for i in texts:
        outs += str(csvText(i)) + ','
    return outs.strip(',')  # removes the last comma so i don't have to fence-post it


def save(text, out, csvStyle=False):
    """writes text to out (file name), can also write it in a csv format\n
accepts strings, lists, and lists of lists"""    
    x = open(out, 'w', encoding='utf-8')
    if type(text) is str:
        if csvStyle:
            text = csvText(text)
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


def numberSTorRD(number):
    """Returns a string with the proper st or rd (1st, 2nd, 3rd, 4th, etc)"""
    if number == 1:
        return str(number) + 'st'
    if number == 2:
        return str(number) + 'nd'
    if number == 3:
        return str(number) + 'rd'
    return str(number) + 'th'


def fileSortScore(string):
    """Gives a specific score to each file name to help with numerical ordering"""
    numbers = [int(i) for i in findall('[0-9]+', string)[:4]]  # only keep track of at most 4 numbers within the string for scoring
    score = 0
    for i in range(len(numbers)):
            score += numbers[i] * (100**(len(numbers) - i))  # some value that should be large enough to prevent overlap between different numbers
    return score

def isFlagSet(flag):
    """Checks weather a specific argument appears within sys.argv and removes it"""
    index = 0
    try:
        index = sys.argv.index(flag)
    except ValueError:
        return False
    del sys.argv[index]
    return True


####################
## MAIN FUNCTIONS ##
####################


def pdfToImages(imageQuality = IMAGE_QUALITY):
    """Convert each page of a pdf to an image and save to imageFolder"""
    global pdfPath, startPage, endPage, poppler_path, imageFolder  # requires these from the global scope but doesn't modify them
    try:
        os.mkdir(imageFolder)
    except:
        print(' Images in', imageFolder)
    # Image output naming convention: pageNum.png
    for pageNum in range(startPage, endPage + 1):
        print('  Imaging page', str(pageNum) + '...')
        page = convert_from_path(pdfPath, imageQuality, first_page = startPage, last_page = endPage, poppler_path = poppler_path, thread_count = PDF_2_IMAGE_THREADS)[0]
        page.save(imageFolder + '\\' + str(pageNum) + '.' + IMAGE_FILE_TYPE)


def getImages():
    """Load images into memory (from imageFolder) that pdf2image created"""
    os.chdir(imageFolder)

    nameList = [file for file in os.listdir() if file[-len(IMAGE_FILE_TYPE):].upper() == IMAGE_FILE_TYPE]
    images = []
    nameList.sort(key = fileSortScore)
    dPrint(nameList)
    for fileName in nameList:
        image = cv2.imread(fileName)
        try:
            image = image[..., ::-1]  # gets image into correct format; also a good check to ensure image is correctly read in
        except:
            raise Exception('Image is incorrect. Check the path provided: ' + imagePath)
        images.append(image)

    os.chdir('..')  # move back into working directory
    return images


def getLayouts(images):
    """Uses the layout parser tool to select select all regions from an image"""

    global textLabel  # requires this from the global scope but doesn't modify it

    model = lp.Detectron2LayoutModel(config_path = config_path,
                                     model_path = model_path,
                                     extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.75],
                                     label_map = {1:"TextRegion", 2:"ImageRegion", 3:"TableRegion", 4:"MathsRegion", 5:"SeparatorRegion", 6:"OtherRegion"})
    textLabel = 'TextRegion'
    layouts = []
    for image in images:
        layout = model.detect(image)
        if len(layout) < 1:
            raise Exception('No regions found in the image')
        layouts.append(layout)
    return layouts


def getTextRegions(layouts):
    """Remove all regions that aren't text regions"""
    textRegions = []
    area = lambda regionObj : regionObj.block.height * regionObj.block.width
    
    for layout in layouts:
        pageTextRegions = lp.Layout([b for b in layout if b.type==textLabel])  # grab everything that is a text region
        pageOtherRegions = lp.Layout([b for b in layout if b.type!=textLabel])
        # Remove text regions that reside within regions of other types
        pageTextRegions = lp.Layout([region for region in pageTextRegions if not any(region.is_in(otherRegion) for otherRegion in pageOtherRegions)])

        # Remove text regions that overlap with other text regions
        # The smaller regions are removed to avoid redundant OCR
        pageTextRegions = lp.Layout([region for region in pageTextRegions if not any(region.is_in(otherRegion) and area(region) < area(otherRegion) for otherRegion in pageTextRegions)])
        textRegions.append(pageTextRegions)
        
    return textRegions


def ocr(textRegions, images):
    """Run optical character recognition on the image to extract text from it"""
    ocrAgent = lp.TesseractAgent(languages='eng')
    texts = []
    for pageNum in range(len(textRegions)):
        print(' ' + numberSTorRD(pageNum + 1), 'Page...')  # pageNum+1 because index starts at 0
        regions = []
        image = images[pageNum]
        for region in textRegions[pageNum]:
            segmentImage = (region
                               .pad(left=5, right=5, top=5, bottom=5)
                               .crop_image(image))  # add padding in each image segment can help improve robustness
            regionText = ocrAgent.detect(segmentImage)
            region.set(text=regionText, inplace=True)
            regions.append(region)
        texts.append(lp.Layout(regions).get_texts())
    return texts


def delImages():
    """Removes images after running to free up space"""
    os.chdir(imageFolder)
    for file in os.listdir():
        os.remove(file)
    os.chdir('..')
    os.rmdir(imageFolder)


def addPageLabels(text):
    """Adds labels to the final output to indicate when pages and regions change"""
    for page in range(len(text)):
        for section in range(len(text[page])):
            text[page][section] += '\n-SECTION END-\n'
        text[page].append('\n--- PAGE END ---\n')
    return text


def getSettings(quiet = False):
    """Set all the apropriate global variables needed for later functions. See the global line or comment in main to see everything it modifies"""
    global workingDir, pdfPath, startPage, endPage, delImages, useCache, imageFolder, outTextPath, imageOnly  # modifies all of these
    if quiet:
        if isFlagSet('-d') or isFlagSet('--delImages'):
            delImages = True
        if isFlagSet('-c') or isFlagSet('--cache'):
            useCache = True
        if isFlagSet('-i') or isFlagSet('--imageOnly'):
            imageOnly = True
        workingDir = sys.argv[1]
        pdfPath = sys.argv[2]
        startPage = sys.argv[3]
        endPage = sys.argv[4]
        assert(os.path.isdir(workingDir))
        os.chdir(workingDir)
        assert(os.path.isfile(pdfPath))
        startPage = int(startPage)
        endPage = int(endPage)
        
    else:
        workingDir = input('Folder Name\n> ')
        while not os.path.isdir(workingDir):
            workingDir = input('Please enter a valid folder name\n> ')
        os.chdir(workingDir)

        pdfPath = input('Pdf Name\n> ')
        while not os.path.isfile(pdfPath):
            print(set(os.listdir()))
            pdfPath = input('Please enter a valid pdf name\n> ')
        startPage = input('Start Page\n> ')
        while True:
            try:
                startPage = int(startPage)
                break
            except:
                startPage = input('Please enter a valid start page\n> ')
        endPage = input('End Page\n> ')
        while True:
            try:
                endPage = int(endPage)
                break
            except:
                endPage = input('Please enter a valid start page\n> ')
                
    imageFolder = pdfPath[:-4] + '-images'  #len('.pdf') == 4
    outTextPath = pdfPath[:-4] + '-transcribed.txt'


##########
## MAIN ##
##########
def main():
    quiet = False
    if len(sys.argv) != 5:  # number of args required
        quiet = True
    else:
        print('Command line usage: python', sys.argv[0], '[options] pdfDirectory pdfName startPage endPage')
        print('  Options: (assume opposite behavior is default)')
        print('\t --delImages | -d \t delete images after running (aka don\'t keep a cache)')
        print('\t --cache     | -c \t use an existing image cache')
        print('\t --imageOnly | -i \t only create images from pdf, don\'t do ocr')
        print('')

    getSettings(quiet)  # side effects: sets workingDir, pdfPath, startPage, endPage, delImages, useCache, imageFolder, outTextPath
                        # modifies current directoy

    if not useCache:  # we aren't using cache, therefore we need to build images
        print('\n\n#Converting PDF to Images#', flush = True)
        pdfToImages()
    if imageOnly:
        print('Created Images, exiting now')
        exit(0)

    print('\n\n#Loading Images#', flush = True)
    images = getImages()

    print('\n\n#Finding Layouts#', flush = True)
    layouts = getLayouts(images)  # side effect: sets textLabel

    print('\n\n#Finding Text Blocks#', flush = True)
    textRegions = getTextRegions(layouts)

    print('\n\n#Running OCR#', flush = True)
    text = ocr(textRegions, images)

    text = addPageLabels(text)

    save(text, outTextPath)

    if delImages:
        delImages()



if __name__ == '__main__':
    main()

"""
    Some debugging information for layout-parser
        model params:
            config_path  -  yaml file for the model; includes info that i don't know how to change
            model_path   -  pth file with model weights; includes info that i REALLY don't know how to change
            extra_config -  MODEL.ROI_HEADS.SCORE_THRESH_TEST is the score threshold to determine if a specific region should be kept; default is .5
                there are other things we can set here, but the documentation on it is hard to find
            label_map    -  map that indicates what each region found by the model means

        model.detect is the line that actually creates a layout object with the supplied file

        common issues with this library/function include:
            DLL issues  -  ensure that the pythoncom37.dll and files aren't found multiple times in the PATH
                see https://github.com/mhammond/pywin32/issues/1709 and https://github.com/Azure/azure-cli/issues/17986

            OSError: [Errno 22] Invalid argument: 'C:\\Users\\USER/.torch/iopath_cache\\s/h7th27jfv19rxiy\\model_final.pth?dl=1.lock'
            pytorch issues  -  ensure the model weights are correctly downloaded and/or loaded; may also be an issue with pytesseract
                see https://stackoverflow.com/questions/68094922/pytorch-throws-oserror-on-detectron2layoutmodel

"""
