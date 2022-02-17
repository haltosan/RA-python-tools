import os
import sys
print('I am alive :)')
import torch
import numpy
import re
import cv2
from math import ceil
from time import sleep

import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\Tesseract-OCR'   # had to change it because of permission issues...
pytesseract.pytesseract.tesseract_cmd = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\Tesseract-OCR\tesseract.exe'
import layoutparser as lp



CONFIG = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\layoutParser\primaLayout\config.yaml'
MODEL = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\layoutParser\primaLayout\model_final.pth'
LABEL_MAP ={1:"TextRegion", 2:"ImageRegion", 3:"TableRegion", 4:"MathsRegion", 5:"SeparatorRegion", 6:"OtherRegion"}
TEXT_LABEL = 'TextRegion'
lpModel = lp.Detectron2LayoutModel(config_path = CONFIG,
                                   model_path = MODEL,
                                   extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.75],
                                   label_map = LABEL_MAP)
ocrAgent = lp.TesseractAgent(languages='eng')
currentBatch = []

IMAGE_FILE_TYPE = 'JPG'
SAVE_FILE_PATH = r'V:\FHSS-JoePriceResearch\papers\current\tree_growth\US\Skagit\skagit_obits\1_Layout_Parser_Code\saves'
#SAVE_FILE_PATH = r'C:\Users\sks239\Desktop'

TASK_BATCH_STRING = ''
CURRENT_PROGRESS = 0
globalCount = 0


## helper functions ##


def log(level, message, end = '\n'):
    message = '[' + level.upper() + ']\t' + message
    try:
        logNumber = TASK_BATCH_STRING.split('-')[-1]
        logName = logNumber + '-lp.log'
        logPath = os.path.join(SAVE_FILE_PATH, logName)
        with open(logPath, 'a') as x:
            x.write(message + end)
    except:
        print('log failure')
        sleep(5)
        try:
            with open(logPath, 'a') as x:
                x.write(message + end)
        except:
            print('secondary log failure')
            sleep(5)
            try:
                with open(logPath, 'a') as x:
                    x.write(message + end)
            except Exception as e:
                print('final log failure')
                print('exception:', e)
                print('location:', logPath)

def timedRetry(command, errorMessage, sleepTime = 5, shouldReturn = False):
    try:
        exec(command)
    except:
        log('warning', errorMessage + ' [1st fail]')
        sleep(sleepTime)
        try:
            exec(command)
        except:
            log('warning', errorMessage + ' [2nd fail]')
            sleep(sleepTime)
            try:
                exec(command)
            except Exception as e:
                log('critical', errorMessage + ' [last fail]')
                raise e

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
    global globalCount
    localCount = 0
    try:
        dirList = [x[0] for x in os.walk('.')]
    except:
        log('warning', 'couldn\'t get dir listing in getImages()')
        sleep(5)
        try:
            dirList = [x[0] for x in os.walk('.')]
        except:
            log('warning', 'couldn\'t get dir listing in getImages() again')
            sleep(5)
            try:
                dirList = [x[0] for x in os.walk('.')]
            except Exception as e:
                log('critical', 'dir os.walk failed in getImages()')
                raise e
    for directory in dirList:
        try:
            nameList = [file for file in os.listdir(directory) if file[-len(IMAGE_FILE_TYPE):].upper() == IMAGE_FILE_TYPE]  # filter the image files only
        except:
            log('warning', 'os.listdir failed once')
            sleep(5)
            try:
                nameList = [file for file in os.listdir(directory) if file[-len(IMAGE_FILE_TYPE):].upper() == IMAGE_FILE_TYPE]
            except:
                log('warning', 'os.listdir failed twice')
                sleep(5)
                try:
                    nameList = [file for file in os.listdir(directory) if file[-len(IMAGE_FILE_TYPE):].upper() == IMAGE_FILE_TYPE]
                except Exception as e:
                    log('critical', 'os.listdir failed in getImages()')
                    raise e
        nameList.sort(key=fileNameSort)  # put it in a reasonable order
        for name in nameList:
            # skip this image if it was completed by a previous run of main()
            
            if localCount < globalCount:
                localCount += 1
                continue

            global imageName
            imageName = os.path.join(directory,name)
            
            print(imageName)

            # start image failsafe
            try:
                image = cv2.imread(imageName)
                image = image[..., ::-1]
                yield image
            except GeneratorExit as e:
                log('Warning','Generator failed...skipping image')
                raise e
            except:  # this try/catch section is for when the remote drives get disconnected; it allows a small pause to reconnect
                sleep(5)
                image = cv2.imread(imageName)
                log('warning', 'Image failed: ' + str(imageName))
                try:
                    image = image[..., ::-1]
                    yield image
                except:
                    log('warning', 'Image failed again: ' + str(imageName))
                    sleep(5)
                    image = cv2.imread(imageName)
                    try:
                        image = image[..., ::-1]
                        yield image
                    except Exception as e:
                        log('critical', 'Image completely failed: ' + str(imageName))
                        raise Exception('The image failed to load: ' + str(imageName))
            # end image failsafe
            globalCount += 1
            localCount += 1


def getTexts(image):
    return ocr(getTextRegions(image), image)


def isGibberish(text): # looks for keywords in the OCR'd text. If none found, assumes the output is gibberish because the image is the wrong way
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
        segment = ocrAgent.detect(segmentedImage)
        texts.append(segment)
    return texts


def rotateImage(image):
    try:
        rotatedImage = numpy.rot90(image)
        return rotatedImage
    except:
        log('warning','Image failed to rotate...returning original')
    return image


def rotateIter(image, rotateCount):
    for i in range(rotateCount):
        image = rotateImage(image)
    return image


def appending_save(texts):
    global CURRENT_PROGRESS
    combinedText = '\n'.join(texts)
    currentBatch.append(combinedText)
    batchNumber = TASK_BATCH_STRING.split('-')[-1]
    fileName = batchNumber + '-save.txt' # make the save file have a name unique to the directory
    filePath = os.path.join(SAVE_FILE_PATH, fileName)
    if len(currentBatch) > 4: # output every time it reads five images
        log('info', 'writing batch ' + str(CURRENT_PROGRESS))
        CURRENT_PROGRESS += 1
        try:
            append(currentBatch, filePath)
        except FileNotFoundError:
            log('warning', 'Save file not found')
            sleep(5)
            try:
                append(currentBatch, filePath)
            except FileNotFoundError:
                log('warning', 'Save file not found again')
                sleep(5)
                try:
                    append(currentBatch, filePath)
                except FileNotFoundError:
                    log('critical', 'Trying save file one more time before succumbing to a critical error...')
                    sleep(15)
                    append(currentBatch, filePath)


def append(currentBatch, filePath):
    with open(filePath, 'a') as x:
        x.write('\n'.join(currentBatch))
        currentBatch.clear()


def main():
    print('Main reached')
    global TASK_BATCH_STRING

    imageNumber = 0
    if len(sys.argv) < 2:
        print("usage: " + sys.argv[0] + " [image directory]")
        exit(1)
    workingDir = sys.argv[1]
    TASK_BATCH_STRING = workingDir.split('-')[-1]  # get the number that comes after the '-'
    os.chdir(workingDir)
    previousRotation = 0
    for image in getImages():
        image = rotateIter(image, previousRotation) # set image to the orientation of the previous image (often matches)
        texts = getTexts(image)
        rotateCount = 0
        while isGibberish(texts) and rotateCount < 4: # if the output is gibberish, try rotating the image up to 3 times to get correct orientation
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




log('start', '***\n\n')
try: # run main up to 3 times to allow for drive issues; each run skips to the place the previous one left off
    main()
except Exception as e:
    print('main failed. Message:',e)
    log('warning', 'main failed on image count ' + str(globalCount) +  ', with this exception:\n' + str(e))
    sleep(15)
    print('Trying main again...')
    try:
        main()
    except Exception as ex:
        log('warning', 'main failed again on image count ' + str(globalCount) +  ', with this exception:\n' + str(ex))
        sleep(15)
        print('Trying main again...')
        try:
            main()
        except Exception as exep:
            log('critical', 'main failed for the 3rd time on image count ' + str(globalCount) + ', with this exception: ' + str(exep))
            log('critical', 'The previous two errors were (in order):\n' + str(e) + '\n' + str(ex))

log('end', 'The script has finished running')
