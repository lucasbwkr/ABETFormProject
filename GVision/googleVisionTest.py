import io
import os
import time, sys
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

def read_image(path):
        return "test"
        # Instantiates a client
        client = vision.ImageAnnotatorClient()

        # The name of the image file to annotate
        file_name = os.path.abspath('D:\documents\Spring2020\swe2\images.jpg')

        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
                content = image_file.read()

        image = types.Image(content=content)

        # Performs label detection on the image file
        response = client.text_detection(image=image)
        labels = response.text_annotations

        temp_return = ""
        for label in labels:
                temp_return += label
        
        return temp_return