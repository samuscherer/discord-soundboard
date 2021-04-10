#Sound Lib

import datetime
import os

sounddir = "./sounds/"
imagedir = "./images/"
savedir = "./saves/"
savefile = "soundbitch_db.csv"
sdict={}

class Sound:

    soundstotal = 0
    uid = 0

    def __init__(self, sid, name, cat, date, cntr):
        self.sid = sid
        self.name = name
        self.cat = cat
        self.date = date
        self.counter = cntr

        Sound.soundstotal += 1
        Sound.uid +=1
    
    def __del__(self):
        pass                            #Destruktor später auscoden!!!!!!!!!!!!!!!!!! ( . Y . )
        Sound.soundstotal -= 1          #Exception Handling (Neg Werte)
        
    def path_to_sound(self):
        return sounddir + self.cat + "/" + self.name
    def path_to_image(self):
        return imagedir + self.cat + "/" + self.name
    def get_song_length(self):
        pass                            #Später auscoden!!!!!!!!!!!!!!!!!!! ( . Y . )



def import_sounds_from_fs():                    #Initialize sound dictionary from sound directory
    raw_files = os.listdir(sound_dir)           #list all elements in sound directory
    for raw_file in raw_files:                  #Iterate elements
        if os.path.isdir(sound_dir+raw_file):   #Check if element is a directory
            sdict[raw_file]=[]             #Add folder name as key paired with an empty souunds list to sound dictionary
    folder_dict_keys=sdict.keys()          #Write keys to temp iterable
    for folder_key in folder_dict_keys:         #Loop through keys
        raw_sound_list = os.listdir(sounddir+folder_key+"/")            #write list with all elements in category folder
        object_sound_list = []                                          #create empty list for sound objects
        for sound in raw_sound_list:                                    #loop through the soundfiles in current category
            object_sound_list.append(Sound(1, sound, folder_key, date.today()))       #append sound object to category list
        sdict[folder_key] = object_sound_list          #pair category key with sound object list
    for folder_key in folder_dict_keys:
        for folder_element_index,folder_element in enumerate(sdict[folder_key]):
            sdict[folder_key][folder_element_index]=folder_element[:folder_element.rfind(".")]

def update_sdict():
    pass

def simport(sdict):
    pass

def sexport(sdict):
    pass

def list_cat(cat):
    pass

def gen_list():
    pass

def remove_sound(sound):
    pass

def restore_sound(sound):
    pass

def clear_sounds():
    pass

def move_sound():
    pass

def check_path():
    pass



s1 = Sound(1234, "test1", "cat1", 20210122, 0)

print(s1.name)
print(s1.path_to_sound())
print(s1.path_to_image())