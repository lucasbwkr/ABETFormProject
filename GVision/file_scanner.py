from os import walk
from typing import List

class Folder:
        ''' Summary ::  A single directory path and every valid image file it contains

            Details ::  This class will take files, directory, and its root save path
                        and records the number of files, each save path, and the files
                        results via the "get_file_save_dist" function
        '''
        def __init__(self, files, directory, save_dist):
                """Function constructure"""
                self.files = self.get_valid_files(files)
                self.directory = directory
                self.save_dist = save_dist
                self.num_of_files = len(files)
                #file_output_result default value is none until stored later
                self.file_output_result = ["None"] * len(files) 

        def save_output_result(self, file : str, result : str):
                """a Setter for File_ourput_results. Populates the correct index to ensure parrel arrays """
                self.file_output_result[self.files.index(file)] = result

        def get_file_save_dist_by_index(self, index : int) -> str:
                """a Setter for File_ourput_results. Populates the correct index to ensure parrel arrays """
                filename = self.files[index].split('.')[0]
                return self.save_dist+"/"+filename+"_result.txt"
        
        def get_file_save_dist(self, old_filename : str) -> str:
                """Takes a file and uses its name to create the result.txt file"""
                filename = old_filename.split('.')[0]
                return self.save_dist+"/"+filename+"_result.txt"

        def get_valid_files(self, files : List[str]) -> List[str]:
            """Loops through initial files list and save the ones with correct format"""
            new_file = []
            for file in files:
                if self.is_image_file(file):
                    new_file.append(file)
            
            return new_file

        def is_image_file(self, file_name : str) -> bool:
            if(file_name == '.DS_Store'):
                return False
            #TODO create a function and will check for invalid files
            return True
        
        def __repr__(self):
                #This is to override default object print value. Use by x = Folder(x,y,z) then 'x' would would print this message
                result_string = "Original Dir: " + self.directory + "\n'Save to' dir: " + self.save_dist + "\nfiles : ["
                for x in self.files:
                        result_string += x + ", "
                result_string += "]"

                return result_string
        
        def __str__(self):
                #This is to override str(Folder) similiar to .toString in java
                result_string = "  **  Original Dir: " + self.directory + "\n  **  'Save to' dir: " + self.save_dist + "\n  **  files : ["
                for x in self.files:
                        result_string += x + ", "
                result_string += "]\n  **  File Results :\n{ \n"
                for x in self.file_output_result:
                        result_string += "        - " + x + ",\n"
                result_string += "}"
                
                return result_string

class DirTree:
        ''' Summary ::  Main directory tree class. It will create a directory tree from root path.

            Details ::  Given a from and save to directory path it fill "walk" through every folder 
                        saving each folder and their files in a Folder Object. Keeping track of Folder
                        and file count. 
        '''
        def __init__(self, path, dist):
                path = path.replace("\\", "/")
                dist = dist.replace("\\", "/")
                self.rootPath = path
                self.dist = self.build_default_dist(dist)
                self.folders = self.get_dir_contents()
                self.folder_count = len(self.folders)
                self.file_count = self.get_file_count()
                

        def get_file_count(self):
                #counts number of files in each folder
                count = 0
                for folder in self.folders:
                        count += folder.num_of_files
                
                return count

        def build_default_dist(self, dist : str) -> str:
                """Creating a default save to directory in case one wasn't selected"""
                #If dist contains an path and it is not the same path as root, accept it
                if dist and dist != self.rootPath:
                        if dist[-1] == "/":
                                return dist[:-1]
                        else:
                            return dist
                #TODO :: Add different logic, if folders are the same create "dist+/result/" as save path
                #If dist was not given or is the same as dir. Create new dist with same name but "_result/" appended 
                folders = self.rootPath.split("/")
                addin = "_Result"
                dist = ''
                array_size = len(folders)
                i = 0
                while i < array_size - 1:
                        dist += folders[i]+"/"
                        i += 1
                
                dist += folders[array_size-1] + addin
                return dist

        def get_dir_contents(self) -> List[object]:
                """Main Function for DirTree. This walks through ever file and folder. Creating a list of Folders objects"""
                #TODO :: Create a active updater for the number of files scanned
                folders = []
                for (dirpath, dirnames, filenames) in walk(self.rootPath, topdown=True):
                        dirpath = dirpath.replace("\\","/")
                        folders.append( Folder(filenames, dirpath, dirpath.replace(self.rootPath, self.dist)) )
                
                return folders

        def __str__(self):
                #This is to override str(Folder) similiar to .toString in java
                return_string ="\n::PRINTING SCANNED FOLDERS::\n\nRoot Path: " + self.rootPath + "\nDistination dir: " + self.dist + "\nFolder details:\n{\n\n\n"
                for x in self.folders:
                        return_string+= str(x) + "\n\n\n"
                return_string += "}"
                return return_string