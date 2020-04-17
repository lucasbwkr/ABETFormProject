# ABET Form Scanner
***

## How to use

Install the correct dependencies. Use the command below to install them while in the root directory of the project. I reccomend being in a virtual environment while installing the prerequisites. 

`pip install -r requirements.txt`

First of all we need to supply Google Vision with an authentication token. This is located in the root directory of the project `gVisionAuth.json`. We like to live dangerously, so this is on a public repo. Please don't spend all our credits. Activate it by adding to to your environmental variables. Below is an example for Windows and Linux(BASH). Insert the appropriate path to this project.

Windows: `$env:GOOGLE_APPLICATION_CREDENTIALS="C:\PATH\TO\ABETFormProject\GVision\gVisionAuth.json"`

Linux: `export GOOGLE_APPLICATION_CREDENTIALS=/PATH/TO/ABETFormProject/GVision/gVisionAuth.json`

Mac: ?? (sorry)


If all went well to here, you should be able to run the project. 

`cd GVision`

`python main.py`

Once you see the GUI load up we have provided sample forms to scan. These are located in `ABETFormProject/Forms/`. The input folder contains ten complete forms to scan. Select the output folder as a convenient destination. Then click begin in the lower right. With any luck, you'll be given an output showing various graphical representations of the data. Yay!

## Use Case

This program is intended to be used by OU adminstrators to record the results of the ABET Accreditation process at the end of each semester. Instead of manually tallying up the results of the forms, administrators will be able to use this program to automatically record the results. It outputs a pdf of the count of "Strongly Agree", "Agree", "Neutral", "Disagree", and "Strongly Disagree" answers for each question on an ABET form. 

Administrators can run this program by providing a directory containing all of the ABET forms for a class and providing an output folder. Then, the program will store the previously described pdf in the output folder.

## How we built it

The project is made entirely using various python libraries. Some of the key libraries are featured below.

### Gooey

https://github.com/chriskiehl/Gooey

An interesting project which produces quick and easy to use GUI's in Python. It's primary purpose is to produce a GUI for single purpose applications, such as ours. It has a few basic widgets to fit the IO of various Python scripts, such as taking a in a file or directory.

### Google Vision

https://cloud.google.com/vision

Google Vision is a multi purpose platform for image recognition, OCR, and a few other purposes. What we used it for was it's OCR functionality which allowed us to find keywords/phrases such as "Strongly Agree". Since we used as realistic of data as possible by physically circling forms and scanning them, Google Vision sometimes missed these keywords. To mitigate this problem we created a linear regression algorithm to predict the position of the missing items. This in turned allowed us to find and extract each answer in the form of a bounding box to send to our convolutional neural network.

### Image Recognition

https://www.tensorflow.org/

Google vision was used to identify a bounding box of each answer of a form. We used a convolutional neural network to identify whether these answers were circled or not. The program scans each ABET form and sends the cropped questions to the model to determine if it is circled or not, and then tallies up the results.


The model was created in tensorflow using a 2 Dimensional Convolutional Neural Network with 3 convolutional layers, 3 max pooling layers, and 2 dense layers at the end. The combination of hyperparameters was identified by comparing the results of 1032 different combinations of hyper parameters. The models were trained on a set of forms that we all filled out. The model we used for this project has a validation accuracy of .9969. 
