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

    for bound in bounds:
        meanx = (bound.vertices[0].x + bound.vertices[2].x ) / 2
        meany = (bound.vertices[0].y + bound.vertices[2].y ) / 2
        cropped_images.append(
            image.crop((
                meanx - offsetx, 
                meany - offsety, 
                meanx + offsetx, 
                meany + offsety)))

    return cropped_images

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
                #print(para)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds


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


    