import os

folder_dict={}				#empty dictionary for def init_dict() - function
sound_dir = "sounds/"


def init_dict():			# initiation function: dictionary={key=foldername:value=filelist}
	raw_files=os.listdir(sound_dir)			# manipulates global variable "folder_dict"
	for raw_file in raw_files:
		if os.path.isdir(sound_dir+raw_file)==True:
			folder_dict[raw_file]=[] 
	folder_dict_keys=folder_dict.keys()
	for folder_key in folder_dict_keys:  
		folder_dict[folder_key]=os.listdir(sound_dir+folder_key+"/")
	for folder_key in folder_dict_keys:
		for folder_element_index,folder_element in enumerate(folder_dict[folder_key]):
			folder_dict[folder_key][folder_element_index]=folder_element[:folder_element.rfind(".")]

def getListOfAliases():						# creates a list of all available songfiles in every subfolder
	files_list=[]							# of the given path (e.q: path="sounds/")
	folder_dict_keys=folder_dict.keys()
	for folder_key in folder_dict_keys:
		files_list.extend(folder_dict[folder_key])
	return(files_list)

def getSoundDir():
	return sound_dir