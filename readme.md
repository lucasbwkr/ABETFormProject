# ABET Form Scanner
***

## How to use

Lucas

## Use Case

This program is intended to be used by OU adminstrators to record the results of the ABET Accreditation process at the end of each semester. Instead of manually tallying up the results of the forms, administrators will be able to use this program to automatically record the results. It outputs a pdf of the count of "Strongly Agree", "Agree", "Neutral", "Disagree", and "Strongly Disagree" answers for each question on an ABET form. 

Administrators can run this program by providing a directory containing all of the ABET forms for a class and providing an output folder. Then, the program will store the previously described pdf in the output folder.

## How we built it

Job

### Gooey

Job

### Google Vision

Job

### Image Recognition

Google vision was used to identify a bounding box of each answer of a form. We used a convolutional neural network to identify whether these answers were circled or not. The program scans each ABET form and sends the cropped questions to the model to determine if it is circled or not, and then tallies up the results.


The model was created in tensorflow using a 2 Dimensional Convolutional Neural Network with 3 convolutional layers, 3 max pooling layers, and 2 dense layers at the end. The combination of hyperparameters was identified by comparing the results of 1032 different combinations of hyper parameters. The models were trained on a set of forms that we all filled out. The model we used for this project has a validation accuracy of .9969. 
