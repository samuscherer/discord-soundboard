#%%
from config_reader import ConfigReader
import exceptions as exp


class Sound(): 
    config_file_dict=ConfigReader.read_config_file("config_file.json")

    def __init__(self,name:str,category:str,file_extension:str,counter:int) -> None:     #Sound inheritance from Player (or above class necessary!)
        self.name = name
        self._category = category
        self.file_extension=file_extension
        self.counter = counter                                        #increase +1 in Player-Class!!!

    def __str__(self) -> str:
        return self.name

    @property
    def category(self)->str:
        return self._category

    @category.setter
    def category(self,category:str)->str:
        categories = self.config_file_dict["categories"].keys()
        print(categories)
        if category in categories:
            self._category = category
        else:
            raise exp.NotExistingCategoryError("This category does't exist!")


    @property
    def duration(self)->int:
        pass

    @property
    def storage(self)->str:
        pass

    def call_counter(self)->None:           # maybe not in this class! --> move to baseclass 
        pass





    
# %%
