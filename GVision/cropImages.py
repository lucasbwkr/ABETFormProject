import argparse
from enum import Enum
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
from scipy import stats

#https://cloud.google.com/functions/docs/tutorials/ocr
class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

answerOption = ['strongly disagree','disagree','neutral','agree','strongly agree']

def findAnswerOption(listV):
    if not listV or listV == []:
        return False
    elif listV == [True, True, False, True, False]: #Strongly agree
        return answerOption[0]
    elif listV == [False, True, False, True, False]: #Strongly Disagree
        return answerOption[1]
    elif listV == [False, False, True, False, False]: #Neutral
        return answerOption[2]
    elif listV == [False, False, False, True, False]: #agree
        return answerOption[3]
    else:
        return answerOption[4] #Strongly agree

def crop_box(image, bounds):
    """Draw a border around the image using the hints in the vector list."""
    cropped_images = []
    offsety= 80
    offsetx = 150
    
    tupleSets = []
    # numItems = 0
    # runningMeanX = 0
    # runningSumX = 0
    # runningMeanY = 0
    # runningSumY = 0
    


    for bound in bounds:
        meanx = (bound.vertices[0].x + bound.vertices[1].x + bound.vertices[2].x + bound.vertices[3].x) / 4
        meany = (bound.vertices[0].y + bound.vertices[1].y + bound.vertices[2].y + bound.vertices[3].y) / 4
        
        #tupleSets.append((meanx, meany, bound))
        tupleSets.append((meanx, meany))

        cropped_images.append(
            image.crop((
                meanx - offsetx, 
                meany - offsety, 
                meanx + offsetx, 
                meany + offsety)))

    tupleSets.sort(key = lambda x: x[1])

    tupleGroupingsY = []
    tempAr = []
    for i in range(len(tupleSets) - 1):
        tempAr.append(tupleSets[i])
        if abs(tupleSets[i][1] - tupleSets[i + 1][1]) > 50:
            tempAr.sort(key = lambda x: x[0])
            tupleGroupingsY.append(tempAr)
            tempAr = []
    
    tempAr.append(tupleSets[len(tupleSets) - 1])
    tempAr.sort(key = lambda x: x[0])
    tupleGroupingsY.append(tempAr)

    xSums = [0,0,0,0,0]
    completeLines = len(tupleGroupingsY)
    for i in range(len(tupleGroupingsY)):
        if len(tupleGroupingsY[i]) == 5:
            for j in range(len(tupleGroupingsY[i])):
                xSums[j] += tupleGroupingsY[i][j][0]
        else:
            completeLines -= 1
    
    xMean = [0,0,0,0,0]
    for i in range(len(xMean)):
        xMean[i] = xSums[i] / completeLines

    

    for i in range(len(tupleGroupingsY)):
        if len(tupleGroupingsY[i]) != 5:
            for j in range(len(tupleGroupingsY[i])):
                if abs(tupleGroupingsY[i][j][0] - xMean[j]) > 100:
                    if len(tupleGroupingsY[i]) < 5:
                        edgeInserts(tupleGroupingsY, i, j)
                    print("POP", i, j)

    # https://pythonprogramming.net/how-to-program-best-fit-line-machine-learning-tutorial/


    for item in tupleGroupingsY:
        print(item)
    return cropped_images


def edgeInserts(tupleGroup, i, j):
    if i == 0 and j == 0:
        print(0, 0)
    elif i == 0 and j == 4:
        print(0, 4)
    elif i == 7 and j == 0:
        print(7, 0)
    elif i == 7 and j == 4:
        print(7, 4)
    else:
        print("Not Applicable")

def save_images(images, file_name):
    count = 0

    for image in images:
        temp = (file_name.replace('.','_a'+str(count)+'.'))
        image.save(temp)
        count += 1

def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    paragraphs = []
    lines = []
    breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType
    lastValue = ''
    #https://stackoverflow.com/questions/51972479/get-lines-and-paragraphs-not-symbols-from-google-vision-api-ocr-on-pdf/52086299
    #for page in document.pages:
     #   for block in page.blocks:
      #      for paragraph in block.paragraphs:
       #         para = ""
        #        line = ""
                # for word in paragraph.words:
                #     for symbol in word.symbols:
                #         line += symbol.text
                #         if symbol.property.detected_break.type == breaks.SPACE:
                #             line += ' '
                #         if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                #             line += ' '
                #             lines.append(line)
                #             para += line
                #             line = ''
                #         if symbol.property.detected_break.type == breaks.LINE_BREAK:
                #             lines.append(line)
                #             para += line
                #             line = ''
                # paragraphs.append(para)

    #print(paragraphs)

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                para = ""
                line = ""
                for word in paragraph.words:
                    for symbol in word.symbols:
                        line += symbol.text
                        if symbol.property.detected_break.type == breaks.SPACE:
                            line += ' '
                        if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                            line += ' '
                            lines.append(line)
                            para += line
                            line = ''
                        if symbol.property.detected_break.type == breaks.LINE_BREAK:
                            lines.append(line)
                            para += line
                            line = ''
                if (any(map(para.strip(' \t\n\r').lower().__contains__, answerOption)) and (len(para.strip(' \t\n\r')) < 20) and feature == FeatureType.PARA):
                    # checking for duplicates
                    temp = findAnswerOption(list(map(para.strip(' \t\n\r').lower().__contains__, answerOption)))
                    if lastValue != '' and lastValue == temp:
                        bounds.pop()
                    lastValue = temp
                    bounds.append(paragraph.bounding_box)
                    #print(temp)
                #print(para)

    # The list `bounds` contains the coordinates of the bounding boxes.
    #print (bounds)
    return bounds

# def linearCheck():


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.PARA)
    images = crop_box(image, bounds)
    #temp = image.crop((100, 200, 150, 250))
    #draw_boxes(image, bounds, 'blue')
    #bounds = get_document_bounds(filein, FeatureType.PARA)
    #draw_boxes(image, bounds, 'red')
    #bounds = get_document_bounds(filein, FeatureType.WORD)
    #draw_boxes(image, bounds, 'yellow')
    #temp.show()
    if fileout != 0:
        save_images(images, fileout)
        
    else:
        image.show()

def get_file_answers(file_path, file_dist):
    render_doc_text(file_path, file_dist)


    