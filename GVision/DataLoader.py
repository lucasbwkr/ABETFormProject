import io
import os, webbrowser
import time
import file_scanner as file_scanner
import custom_progressbar as custom_progressbar
import googleVisionTest as GVT
import cropImages as getAnswers
import numpy as np
from typing import List
from os.path import isfile, join
import matplotlib.pyplot as plt
from math import ceil
from pylab import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from tensorflow.keras.models import load_model

FONTSIZE = 18
FIGURE_SIZE = (7,7)

plt.rcParams.update({'font.size': FONTSIZE})
plt.rcParams['figure.figsize'] = FIGURE_SIZE
# Default tick label size
plt.rcParams['xtick.labelsize'] = FONTSIZE - 8
plt.rcParams['ytick.labelsize'] = FONTSIZE

def create_result_folder(folder: object):
    ''' Summary ::  Creates and populates folders and resulting file

        Details ::  This function gets passed a Folder object
                    defined in "File_scanner". From this object
                    It will create the directory and result files
                    given by the Folder structure.
    '''

    # Creates result directory if it doesn't already exists
    if not os.path.exists(folder.save_dist):
        os.mkdir(folder.save_dist)

    # Loops through every file inside structure and writes result into frile.
    for file in folder.files:
        # Creates or truncates files to show result
        f = open(folder.get_file_save_dist(file), "w")
        index = folder.files.index(file)
        f.write(folder.file_output_result[index])
        f.close()


def run_file_through_google_vision(dir_tree: object, dist):
    ''' Summary ::  Passes every valid file in directory tree into
                    a custom built google vision function to validate image 

        Details ::  Loops through every folder in tree to get there files. Then sends each 
                    file into 'googleVisionTest.read_image()' function, and storing the result
    '''
    #TODO ::  might want to change logic when less then 100 files are given
    hashtag_loading_block_size = int(dir_tree.file_count)
    print(hashtag_loading_block_size)

    model = load_model('model.h5')
    start = 0

    questions_per_page = 8
    answers_per_question = 5
    total_result = np.zeros((questions_per_page, answers_per_question))
    for x in dir_tree.folders:
        for y in x.files:
            #x.save_output_result(y, GVT.read_image(x.directory+"/"+y))
            imgs = getAnswers.get_file_answers(x.directory+"/"+y,x.save_dist+"/"+y)

            imgs = [np.asarray(img.convert('L')).reshape(160, 300,1) for img in imgs]
            imgs = np.array(imgs, dtype=np.float32)
            preds = model.predict(imgs)
            preds = preds[:,0]
            preds = preds.reshape((questions_per_page, answers_per_question))
            result = preds > .95
            # print(preds)
            # print(result)  
            for i in range(questions_per_page):
                indices = np.argwhere(result[i] == True)
                if len(indices) > 1:
                    max_idx = np.argmax(preds[i])
                    for j in range(answers_per_question):
                        if j != max_idx:
                            result[i,j] = False
            total_result += result
            # if start % hashtag_loading_block_size == 0:
            #     time.sleep(.01)
            start += 1
            custom_progressbar.update_progress(
                (start/hashtag_loading_block_size))
    
    generate_plots(total_result, dist)

def generate_plots(result, dist):
    answers = ['Strongly\nDisagree','Disagree', 'Netural', 'Agree', 'Strongly\nAgree']
    pdf = PdfPages(dist +'\\ABETresults.pdf')
    i = 1
    for r in result:
        fig = plt.figure()
        yint = range(int(min(r)), int((max(r))+1))
        plt.yticks(yint)
        plt.title('Question ' + str(i))
        plt.xlabel('Answers')
        plt.ylabel('Count')
        plt.bar(answers, r)
        pdf.savefig(fig)
        i += 1
    pdf.close()





def create_result_dir_tree(dir_tree: object):
    ''' Summary ::  Creates and populates directory tree

        Details ::  This function gets passed a DirTree object
                    defined in "File_scanner". From this object
                    It will create the directory and result files
                    for every folder in Folder structure array.
    '''
    hashtag_loading_block_size = int(dir_tree.folder_count/100)
    if hashtag_loading_block_size == 0:
        hashtag_loading_block_size = 1

    start = 0
    for x in dir_tree.folders:
        #create_result_folder(x)
        if start % hashtag_loading_block_size == 0:
            time.sleep(.01)
            custom_progressbar.update_progress(
                (.01*(start/hashtag_loading_block_size)))
        start += 1

def start(path, dist):
    # Getting path name from user
    # TODO : Add a directory GUI chooser so we can ensure valid paths are chosen
    path = path
    # Get destination, If same or empty it is given then it renames top PATH
    dist = dist

    print("\nScanning Files . . .")
    # Creates a file tree. Walking through every folder and collecting the name and location of every file
    # Via an array of folders objects
    dir_tree = file_scanner.DirTree(path, dist)

    # Prints number of directories and files
    print("\nNumber of Directories Scanned . . . " +
        str(dir_tree.folder_count) + "\n")
    print("Number of Files Scanned :: " + str(dir_tree.file_count) + "\n")

    print("\nCalulating Scanned Files :: \n")
    run_file_through_google_vision(dir_tree, dist)

    print("\n\nOutputting Results . . .\n")
    create_result_dir_tree(dir_tree, )
    # Opening Dist Folder
    # webbrowser.open('file:///' + dist)
    webbrowser.open('file:///' + dist + '\\ABETresults.pdf')