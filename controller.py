#%%
from sound import Sound
from config_reader import ConfigReader
import exceptions as exp
import os
import numpy as np
import pickle
import time
import shutil

class Controller():
    object_sound_list = []
    config_file = ConfigReader.read_config_file('config_file.json')
    category_list = np.array([])

    @classmethod
    def cat_list_generator(cls)->None:
        """This function edits the class-attribute 'category_list' and fills it with all available categories
        which are defined in the song-object-category attributes. 

        """
        for sound_obj in cls.object_sound_list:
            cls.category_list = np.append(cls.category_list,sound_obj.category)
        cls.category_list = np.unique(cls.category_list)
        cls.category_list = np.sort(cls.category_list)

    @classmethod
    def import_sounds_from_fs(cls,sound_folder):
        sound_dict={}
        raw_files = os.listdir(sound_folder)                            #list all elements in sound directory
        for raw_file in raw_files:                                      #Iterate elements
            if os.path.isdir(sound_folder+raw_file):                    #Check if element is a directory
                sound_dict[raw_file]=[]                                 #Add folder name as key paired with an empty sounds list to sound dictionary
        folder_dict_keys=sound_dict.keys()                              #Write keys to temp iterable
        for folder_key in folder_dict_keys:                             #Loop through keys
            raw_sound_list = os.listdir(sound_folder+"/"+folder_key+"/")            #write list with all elements in category folder
            for sound in raw_sound_list:                                            #loop through the soundfiles in current category
                file_extension=sound[sound.rfind("."):]                 #read out file_extension
                sound=sound.replace(file_extension,"")                  #remove file_extension from sound-file
                cls.object_sound_list.append(Sound(sound,folder_key,file_extension,counter=0))    #append sound object to list

    @staticmethod
    def export_save(save_folder)->int:
        """ This function handles the save_file exports
            - creates the save_folder if it does not exist
            - Serializes the song_object_list with pickle and dumps it to save_file
            - Deletes oldest save_file when reaching the defined maximum
            
            Args:
                save_folder (str):      save_folder location relative to run.py location

            Raises: 
                ------- Add Raise once you know how to do that properly @Andi ------ 
                
            Returns:
                False in Error case
                True in nominal case
        """
        try:
            if not os.path.exists(save_folder):
                os.mkdir(save_folder)
            filename = "./" + save_folder + "/" + Controller.config_file['save_name']
            list_of_save_files = os.listdir(Controller.config_file['savefile_folder'])
            list_of_save_files = [f"./{save_folder}/{save_file}" for save_file in list_of_save_files]
            if os.path.isfile(filename):
                shutil.copy2(filename, filename + "_" + time.strftime("%Y%m%d-%H%M%S"))
            if len(list_of_save_files) >= Controller.config_file['num_of_savefiles']:
                os.remove(min(list_of_save_files, key=os.path.getctime))
            outfile = open(filename, 'wb')
            pickle.dump(Controller.object_sound_list, outfile)
            outfile.close()
            return True
        except:
            return False

    def import_save(save_folder)->int:
        """ This function handles the save_file import
            - checks if save_file exists
            - Deserializes the song_object_list with pickle and writes it back to song_object_list
            
            Args:
                save_folder (str):      save_folder location relative to run.py location
                
            Returns:
                False in Error case
                True in nominal case
        """
        filename = "./" + save_folder + "/" + Controller.config_file['save_name']
        if os.path.isfile(filename):
            infile = open(filename, 'rb')
            Controller.object_sound_list = pickle.load(infile)
            infile.close()
            return True
        else:
            return False
    
    # def save_file_fs_integrity_check(save_folder)->bool:
    #     object_list_from_fs = Controller.import_sounds_from_fs(save_folder)
    #     if hash(Controller.object_sound_list) == hash(object_list_from_fs):
    #         return True
    #     else:
    #         return False

    @staticmethod
    def path_generator(command:str)->str:       #move to Song-Class! (maybe)
        """This function creates a path to a song-object which can be used for the 
        discord 'play-function'. 

        Args:
            command (str): Composition between sound_command and songobject.name (e.g.: '!actionreaction')
                            --> the sound_command-marker will be removed by the function itself!

        Raises:
            exp.SoundNotFoundError: If the sound is not in the object_sound_list the exception will be raised!

        Returns:
            str: contains the relative path to the file starting with the sound-folder
        """
        sliced_command=command[1:]
        for sound_obj in Controller.object_sound_list:
            if sound_obj.name==sliced_command:
                return(f"{Controller.config_file['sound_folder']}{sound_obj.category}/{sound_obj.name}{sound_obj.file_extension}")    
        raise exp.SoundNotFoundError(f"The sound '{command}' does not exist!")
        

    @staticmethod
    def song_list_generator(command:str,invoker=False,as_object=False)->list:
        """This function creates a list with all song-objects which have the same                   # CHANGE DOCSTRING-DESCRIPTION!!!
        value defined in the category-attribute.

        Args:
            command (str): Composition between list_command and category-name (e.g.: "list HandOfBlood")
                            --> the list_command is defined in the config_file

        Raises:
            exp.CatNotFoundError: If the category does not exist, the CatNotFoundError will be raised.
        Returns:
            list: a list which contains all song-objects in a certain category
        """
        command_replacement_list =[" ",Controller.config_file["list_command"],Controller.config_file["invoker"]]   #Define elements which needs to be replaced
        
        if invoker==True:
            as_object=False                                                                 #make sure no invoker is included if object-list is requested

        for command_replacement_value in command_replacement_list:
            command=command.strip().replace(command_replacement_value,"")                   #remove leading/ending whitespace-character and replace replacement-list elements with nothing
        print(command)
        song_list=[]                                                                        #e.g.: command = !list --> len(string)=0, command = !list HandOfBlood --> len(string) != HandOfBlood
        if len(command)!= 0:                                                                #Check if len(command) is not zero
            if command in Controller.category_list:                                         #Check if category exists
                if as_object==False:                                                        #if as_object==False, create song_name_list
                    for sound_obj in Controller.object_sound_list:                          #Iterate all sound objects
                            if sound_obj.category == command:
                                if invoker==True:                                           #Check if soundobject has desired category
                                    song_list.append(Controller.config_file["invoker"]+sound_obj.name)   #Append Invoker+Soundname to list
                                else:
                                    song_list.append(sound_obj.name)                        #Append Soundname to list                                   
                else:                                                                       #if as_object==True, create song_object_list
                    for sound_obj in Controller.object_sound_list:                          #Iterate all sound objects
                        if sound_obj.category == command:                                   #Check if soundobject has desired category
                            song_list.append(sound_obj)                                     #Append Soundnames to list
            else:
                return song_list
        elif len(command) == 0:                                                             #Check if len(command) is zero
            for sound_obj in Controller.object_sound_list:                                  #Iterate all sound objects
                if as_object==False:                                                        #if as_object==False, create song_name_list
                    song_list.append(sound_obj.name)                                        #Append Soundnames to list
                else:
                    song_list.append(sound_obj)                                             #if as_object==True, create song_object_list
        song_list.sort()
        return song_list                                                                    #Return List of desired Sound








# class Mediaplayer:
#     def __init__(self,s_name,path,volume)->None:
#         self.sound=s_name
#         self.path=path
#         self.volume=volume
# 
#     def play_sound(self,s_name,path):
#         print("played sound successfully!")
#     
#     def delete_sound(self,s_name,path):
#         print("deleted sound succesfully!")
# 
#     def add_sound(self,s_name,path):
#         print("added sound successfully!")
#     
#     def change_volume(self,volume):
#         print("volume successfully changed!")
# 
# class Sound(Mediaplayer):
#     def __init__(self,s_name,path,counter,duration,date) -> None:
#         Mediaplayer.__init__(self,s_name,path)
#         self.counter=counter
#         self.duration=duration
#         self.date=date
#         
#     # methods necessary??
# 
# class User:
#     def __init__(self,username,permission) -> None:
#         self.permission=permission
#         self.username=username
# 



# %%
