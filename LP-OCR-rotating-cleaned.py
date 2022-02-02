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
SAVE_FILE_PATH = r'V:\papers\current\tree_growth\US\Skagit\skagit_obits\LP_output\\'



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
    localCount = 0
    dirList = [x[0] for x in os.walk('.')]
    for directory in dirList:
        nameList = [file for file in os.listdir(directory) if file[-len(IMAGE_FILE_TYPE):].upper() == IMAGE_FILE_TYPE]
        nameList.sort(key=fileNameSort)
        for name in nameList:

            # if this image has already been done, skip it
            if localCount < globalCount:
                localCount += 1
                continue

            global imageName
            imageName = os.path.join(directory,name)
            global directoryName
            directoryName = os.path.basename(directory)  # TODO: FIGURE OUT HOW MUCH OF THE DIRECTORY THIS GIVES YOU
            print(imageName)

            image = cv2.imread(imageName)
            # start image failsafe
            try:
                image = image[..., ::-1]
                yield image
            except:  # this try/catch section is for when the remote drives get disconnected; it allows a small pause to reconnect
                sleep(5)
                image = cv2.imread(imageName)
                logging.warning('Image failed: ' + str(imageName))
                try:
                    image = image[..., ::-1]
                    yield image
                except:
                    logging.warning('Image failed again: ' + str(imageName))
                    sleep(5)
                    image = cv2.imread(imageName)
                    try:
                        image = image[..., ::-1]
                        yield image
                    except:
                        logging.critical('Image completely failed: ' + str(imageName))
                        raise Exception('The image failed to load: ' + str(imageName))
            # end image failsafe
            globalCount += 1
            localCount += 1


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

def rotateImage(image):
    try:
        rotatedImage = numpy.rot90(image)
        return rotatedImage
    except:
        logging.warning('Image failed to rotate...returning original')
    return image

def rotateIter(image, rotateCount):
    for i in range(rotateCount):
        image = rotateImage(image)
    return image

def save(text, location):
    with open(location, 'w') as x:
        x.write('\n'.join(text))

def appending_save(texts):
    combinedText = '\n'.join(texts)
    currentBatch.append(combinedText)
    fileName = directoryName + '-save.txt' # make the save file have a name unique to the directory
    filePath = os.path.join(SAVE_FILE_PATH, fileName)
    if len(currentBatch) > 4: # output every time it reads five images
        try:
            append(currentBatch, filePath)
        except FileNotFoundError:
            logging.warning('Save file not found')
            sleep(5)
            try:
                append(currentBatch, filePath)
            except FileNotFoundError:
                logging.warning('Save file not found again')
                sleep(5)
                try:
                    append(currentBatch, filePath)
                except FileNotFoundError:
                    logging.warning('Trying save file one more time before succumbing to a critical error...')
                    sleep(15)
                    append(currentBatch, filePath)



def append(currentBatch, filePath):
    with open(filePath, 'a') as x:
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
            image = rotateImage(image)
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
global globalCount
globalCount = 0

try:
   main()
except Exception as e:
    logging.warning('main failed on image count ' + globalCount +  ', with this exception:\n' + e)
    sleep(15)
    print('Trying main again...')
    try:
        main()
    except Exception as ex:
        logging.warning('main failed again on image count ' + globalCount +  ', with this exception:\n' + ex)
        sleep(15)
        print('Trying main again...')
        try:
            main()
        except Exception as exep:
            logging.critical('main failed for the 3rd time on image count ' + globalCount + ', with this exception: ' + exep)
            logging.critical('The previous two errors were (in order):\n' + e + '\n' + ex)