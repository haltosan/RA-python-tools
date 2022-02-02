import os
import sys
import numpy
import re
import cv2
from math import ceil

import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.path.join(os.environ['USERPROFILE'], 'Desktop\\localTess\\tesseract.exe')
import layoutparser as lp

CONFIG = r'V:\RA_work_folders\Ethan_Simmons\layoutParser\primaLayout\config.yaml'
MODEL = r'V:\RA_work_folders\Ethan_Simmons\layoutParser\primaLayout\model_final.pth'
LABEL_MAP ={1:"TextRegion", 2:"ImageRegion", 3:"TableRegion", 4:"MathsRegion", 5:"SeparatorRegion", 6:"OtherRegion"}
TEXT_LABEL = 'TextRegion'
lpModel = lp.Detectron2LayoutModel(config_path = CONFIG,
                                   model_path = MODEL,
                                   extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.75],
                                   label_map = LABEL_MAP)
ocrAgent = lp.TesseractAgent(languages='eng')
currentBatch = []

IMAGE_FILE_TYPE = 'JPG'
SAVE_FILE_PATH = r'V:\papers\current\tree_growth\US\Skagit\skagit_obits\LP_output\'



## helper functions ##


def fileNameSort(name):  # to be used as a sorting key
    return int(''.join(re.findall(r'\d', name)))

def getTextRegions(image):
    allLayouts = lpModel.detect(image)
    return processRegions([region for region in allLayouts if region.type == TEXT_LABEL])

def processRegions(regions):
    area = lambda regionObj : regionObj.block.height * regionObj.block.width  # area function
    center = lambda textBlock : [ceil((textBlock.block.y_1 + textBlock.block.y_2)/600), (textBlock.block.x_1 + textBlock.block.x_2)/2]
    regionPadding = 70
    
    regions = lp.Layout([region for region in regions if not any(region.is_in(otherRegion) and area(region) < area(otherRegion) for otherRegion in regions)])  # remove subset regions
    for region in regions:  # add region padding (increases size to eliminate times where it cuts off text)
        rect = region.block
        rect.x_1 -= regionPadding  # left is negative
        rect.y_1 -= regionPadding  # up is negative
        rect.x_2 += regionPadding
        rect.y_2 += regionPadding
    regions._blocks.sort(key = center)  # sort regions
    return regions


## main functions ##


def getImages():  # generator for image objects (type np.array)
    dirList = [x[0] for x in os.walk('.')]
    for directory in dirList:
        nameList = [file for file in os.listdir(directory) if file[-len(IMAGE_FILE_TYPE):].upper() == IMAGE_FILE_TYPE]
        nameList.sort(key=fileNameSort)
        for name in nameList:
            global imageName
            imageName = os.path.join(directory, name)
            global directoryName
            directoryName = os.path.basename(directory)  # TODO: FIGURE OUT HOW MUCH OF THE DIRECTORY THIS GIVES YOU
            print(imageName)
            yield cv2.imread(imageName)

def getTexts(image):
    return ocr(getTextRegions(image), image)

def isGibberish(text):
    words = ['died','passed away','born','life','survived','funeral','family','friends','January', 'February','March','April','May','June','July','August','September','October','November','December','Monday','Tuesday','Wednesday','Thursday','Friday', 'Saturday','Sunday','wife','husband','married']
    for textBlock in text:
        for word in words:
            if textBlock.find(word) != -1:
                return False
    return True

def ocr(textRegions, image):
    texts = []
    for region in textRegions:
        segmentedImage = region.pad(left=5, right=5, top=5, bottom=5).crop_image(image)
        texts.append(ocrAgent.detect(segmentedImage))
    return texts

def rotate(image):
    return numpy.rot90(image)

def rotateIter(image, rotateCount):
    for i in range(rotateCount):
        image = rotate(image)
    return image

def save(text, location):
    with open(location, 'w') as x:
        x.write('\n'.join(text))

def appending_save(texts):
    combinedText = '\n'.join(texts)
    currentBatch.append(combinedText)
    # TODO: test new save file naming system
    fileName = SAVE_FILE_PATH + directoryName + '-save.txt' # make the save file have a name unique to the directory
    if (len(currentBatch) > 4): # output every time it reads five images
        with open(fileName, 'a') as x:
            x.write('\n'.join(currentBatch))
            currentBatch.clear()

    
def main():
    imageNumber = 0
    if len(sys.argv) < 1:
        print("[script name] [image directory]")
        exit(1)
    workingDir = sys.argv[1]
    os.chdir(workingDir)
    previousRotation = 0
    for image in getImages():
        image = rotateIter(image, previousRotation)
        texts = getTexts(image)
        rotateCount = 0
        while isGibberish(texts) and rotateCount < 4:
            print('flip',rotateCount)
            image = rotate(image)
            texts = getTexts(image)
            rotateCount += 1
        previousRotation = rotateCount
        # add information to image text before sending it off
        imageNameString = 'IMAGE:' + imageName # add the image name to the bottom of the file
        texts.append(imageNameString)
        texts.append('--- PAGE END ---') # add the separating text
        appending_save(texts)
        imageNumber += 1
        





## running main ##
main()


