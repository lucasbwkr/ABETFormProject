import argparse
from enum import Enum
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

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

    for bound in bounds:
        meanx = (bound.vertices[0].x + bound.vertices[1].x + bound.vertices[2].x + bound.vertices[3].x) / 4
        meany = (bound.vertices[0].y + bound.vertices[1].y + bound.vertices[2].y + bound.vertices[3].y) / 4
        tupleSets.append((meanx, meany))
    # Uncomment this for early exit (avoid running computations)
    #     cropped_images.append(
    #         image.crop((
    #             meanx - offsetx, 
    #             meany - offsety, 
    #             meanx + offsetx, 
    #             meany + offsety)))

    # return cropped_images


    # Form the verticle matrice of values
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


    # Form the horizontal matrice of values
    tupleSets.sort(key = lambda x: x[0])
    tupleGroupingsX = []
    tempAr = []
    for i in range(len(tupleSets) - 1):
        tempAr.append(tupleSets[i])
        if abs(tupleSets[i][0] - tupleSets[i + 1][0]) > 50:
            tempAr.sort(key = lambda x: x[1])
            tupleGroupingsX.append(tempAr)
            tempAr = []
    tempAr.append(tupleSets[len(tupleSets) - 1])
    tempAr.sort(key = lambda x: x[1])
    tupleGroupingsX.append(tempAr)


    for i in tupleGroupingsY:
        print(i)
    
    for i in tupleGroupingsX:
        print(i)

    if (len(tupleGroupingsY) < 8) or (len(tupleGroupingsX)) < 5:
        print("Houston we have a problem")
        return -1
    
    # Calculate vertical slopes and intercepts
    xSumsV = [0,0,0,0,0]
    ySumsV = [0,0,0,0,0]
    xySumsV = [0,0,0,0,0]
    xxSumsV = [0,0,0,0,0]
    completeLinesV = len(tupleGroupingsY)
    for i in range(len(tupleGroupingsY)):
        if len(tupleGroupingsY[i]) == 5:
            for j in range(len(tupleGroupingsY[i])):
                xSumsV[j] += tupleGroupingsY[i][j][0]
                ySumsV[j] += tupleGroupingsY[i][j][1]
                xySumsV[j] += tupleGroupingsY[i][j][0] * tupleGroupingsY[i][j][1]
                xxSumsV[j] += tupleGroupingsY[i][j][0] * tupleGroupingsY[i][j][0]
        else:
            completeLinesV -= 1
    
    if(completeLinesV == 0):
        print("Houston we have a problem.")
        return -1


    xMeanV = [0,0,0,0,0]
    yMeanV = [0,0,0,0,0]
    xyMeanV = [0,0,0,0,0]
    xxMeanV = [0,0,0,0,0]
    slopeV = [0,0,0,0,0]
    interceptV = [0,0,0,0,0]
    for i in range(len(xMeanV)):
        xMeanV[i] = xSumsV[i] / completeLinesV
        yMeanV[i] = ySumsV[i] / completeLinesV
        xyMeanV[i] = xySumsV[i] / completeLinesV
        xxMeanV[i] = xxSumsV[i] / completeLinesV
        slopeV[i] = (xMeanV[i]*yMeanV[i] - xyMeanV[i])/(xMeanV[i]*xMeanV[i] - xxMeanV[i])
        interceptV[i] = yMeanV[i] - slopeV[i]*xMeanV[i]
        # print ("VSlope ", i, ": ",slopeV[i])
        # print("VIntercept ", i, ": ", interceptV[i])
    

    # Calculate horizontal slopes and intercepts
    xSumsH = [0,0,0,0,0,0,0,0]
    ySumsH = [0,0,0,0,0,0,0,0]
    xySumsH = [0,0,0,0,0,0,0,0]
    xxSumsH = [0,0,0,0,0,0,0,0]
    completeLinesH = len(tupleGroupingsX)
    for i in range(len(tupleGroupingsX)):
        if len(tupleGroupingsX[i]) == 8:
            for j in range(len(tupleGroupingsX[i])):
                xSumsH[j] += tupleGroupingsX[i][j][0]
                ySumsH[j] += tupleGroupingsX[i][j][1]
                xySumsH[j] += tupleGroupingsX[i][j][0] * tupleGroupingsX[i][j][1]
                xxSumsH[j] += tupleGroupingsX[i][j][0] * tupleGroupingsX[i][j][0]
        else:
            completeLinesH -= 1

    
    if(completeLinesH == 0):
        print("Houston we have a problem.")
        return -1

    xMeanH = [0,0,0,0,0,0,0,0]
    yMeanH = [0,0,0,0,0,0,0,0]
    xyMeanH = [0,0,0,0,0,0,0,0]
    xxMeanH = [0,0,0,0,0,0,0,0]
    slopeH = [0,0,0,0,0,0,0,0]
    interceptH = [0,0,0,0,0,0,0,0]
    for i in range(len(xMeanH)):
        xMeanH[i] = xSumsH[i] / completeLinesH
        yMeanH[i] = ySumsH[i] / completeLinesH
        xyMeanH[i] = xySumsH[i] / completeLinesH
        xxMeanH[i] = xxSumsH[i] / completeLinesH
        if (xMeanH[i]*xMeanH[i] - xxMeanH[i]) == 0:
            slopeH[i] = 100000000
        else:
            slopeH[i] = (xMeanH[i]*yMeanH[i] - xyMeanH[i])/(xMeanH[i]*xMeanH[i] - xxMeanH[i])

        interceptH[i] = yMeanH[i] - slopeH[i]*xMeanH[i]
        # print ("HSlope ", i, ": ", slopeH[i])
        # print("HIntercept ", i, ": ", interceptH[i])

    


    # https://pythonprogramming.net/how-to-program-best-fit-line-machine-learning-tutorial/
    # Predict positions of answers.
    estimatedPositions = []
    for i in range(8):
        tempAr = []
        for j in range(5):
            tempAr.append(getEstimatedPosition(slopeV[j],slopeH[i],interceptV[j], interceptH[i]))
        estimatedPositions.append(tempAr)


    # Crop the image based upon this estimation
    for i in range(len(estimatedPositions)):
        for j in range(len(estimatedPositions[i])):
            cropped_images.append(
                    image.crop((
                        estimatedPositions[i][j][0] - offsetx, 
                        estimatedPositions[i][j][1] - offsety, 
                        estimatedPositions[i][j][0] + offsetx, 
                        estimatedPositions[i][j][1] + offsety)))

    return cropped_images


def getEstimatedPosition(m1, m2, b1, b2):
    x = (b2 - b1)/(m1 - m2)
    y = (m1*b2-m2*b1)/(m1-m2)
    x = round(x, 1)
    y = round(y, 1)
    return x, y


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
                #     print(temp)
                # print(para)

    # The list `bounds` contains the coordinates of the bounding boxes.
    #print (bounds)
    return bounds

# def linearCheck():


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.PARA)
    
    images = crop_box(image, bounds)
    if fileout != 0:
        if images != -1:
            save_images(images, fileout)
        else:
            print(filein)
        return images
    else:
        image.show()

def get_file_answers(file_path, file_dist):
    return render_doc_text(file_path, file_dist)


    