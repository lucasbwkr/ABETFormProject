import io
import os
import time, sys
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

def read_image(path):

        # Instantiates a client
        client = vision.ImageAnnotatorClient()

        # The name of the image file to annotate
        file_name = os.path.abspath('/Users/jobvillamil/Documents/Spring 2020/SWE2/CS4273Project/forms/cs4273_form.jpeg')

        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
                content = image_file.read()

        image = types.Image(content=content)

        # Performs label detection on the image file
        response = client.text_detection(image=image)
        texts = response.text_annotations

        
        print('Texts:')

        for text in texts:
                print('\n"{}"'.format(text.description))

                vertices = (['({},{})'.format(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices])

                print('bounds: {}'.format(','.join(vertices)))

        if response.error.message:
                raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                        response.error.message))

        temp_return = ""


        #print(temp_return)
        
        return temp_return
