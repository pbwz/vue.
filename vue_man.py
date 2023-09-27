'''
Profile Manager V1.0

Handles profile creation and placement using a legend
file to lookup profiles and other data. Simple attributes
can be saved here such as icons, nicknames, etc. Add any
attributes you would like saved to the ATTRIBUTES tuple.

Dependencies:
    - FileHelper class
    - Profile class

Author: Paul Belland
'''

from file_helper import FileHelper
from vue_prof import Profile
from db import Database
import os

# SETTINGS
MAX_PROFILES = 3
PROF_LEGEND_PATH = './profiles/profiles.txt'
PROF_HOLDER_PATH = './profiles/'
ATTRIBUTES = ['icon','semester']
PROFILE_FILES = ['login.txt']
DB_NAME = 'profile.db'
DB_TABLES = [
    ['Classes',['Class_ID','Semester','Class_Name','Professor','WGPA']],
    ['AE',['Class_ID','AE_ID','AE_Name','AE_Due','AE_Weight','AE_Type','AE_Grade']],
    ]

class ProfileManager:
    '''Profile Manager Class'''
    def __init__(self) -> None:
        self._legend_file = FileHelper(PROF_LEGEND_PATH)
        self._profile_count = 0
        self._preferred_profile = 0
        self._profiles = []
        self._read_legend()   # reads profile legend
        
    def get_all_profiles(self) -> list[Profile]:
        '''Returns all saved profile objects
        
        Input: None
        Return: list[Profile] - profile list'''
        return self._profiles
    
    def get_preferred(self) -> int:
        '''Returns preferred profile number
        
        Input: None
        Return: int - pref profile number'''
        return self._preferred_profile
    
    def get_profile(self,name:str) -> Profile:
        '''Returns an individual specified profile object
        
        Input: None
        Return: Profile object'''
        for profile in self._profiles:
            if profile.get_name() == name:
                return profile

    def set_preferred(self,number:int) -> str:
        '''Sets which profile is preferred or
        removes the current profile from preferred if
        same number is passed
        
        Input: int - fav number
        Return: str - change made'''
        if self._preferred_profile == number:
            self._preferred_profile = 0
            self._write_legend()
            return 'Profile unfavourited'
        else:
            self._preferred_profile = number
            self._write_legend()
            return 'Profile favourited'

    def new_profile(self,name:str,password:str,attributes=[]) -> str:
        '''Adds a new profile with its own legend attributes.
        Depending on success, will return result string.
        
        Input: str - name, str - password, list[str] - attribs
        Return: str - result string'''
        response = self._new_profile_check(name, attributes)
        
        if response == True:
            prof_db = self._new_profile_directory(name)
            
            # create object
            new_profile = Profile(name, prof_db)
            for i in range(len(attributes)):
                new_profile.add_attribute(ATTRIBUTES[i],attributes[i])
                
            # update legend
            self._profiles.append(new_profile)
            self._write_legend()
            new_profile.initialize_login_file(password) # setup for password
            return 'Creation successful'
        else:
            return 'Creation failed'
        
    def _read_legend(self) -> None:
        '''Reads profile legend file
        
        Input: None
        Return: None'''
        raw_data = self._legend_file.read_file()  # read file
        self._profile_count = len(raw_data)  # get count
        
        # get preferred if exists
        preferred = int(raw_data.pop(0))
        if preferred != 0:
            self._preferred_profile = preferred
        
        # get all profile data
        if self._profile_count > 0:
            for profile_info in raw_data:
                profile_info = profile_info.split(',')
                name = profile_info.pop(0)
                db = Database(f'{PROF_HOLDER_PATH}/{name}/{DB_NAME}')
                profile = Profile(name, db)
                
                # get attributes
                for i in range(len(profile_info)):
                    profile.add_attribute(ATTRIBUTES[i],profile_info[i])
                self._profiles.append(profile)
                
    def _write_legend(self) -> None:
        '''Writes all basic profile manager data
        back to the legend file
        
        Input: None
        Return: None'''
        # write preferred
        self._legend_file.write_file(f'{self._preferred_profile}')
        
        # write indiv profiles
        for profile in self._profiles:
            name = profile.get_name()
            attrib_dict = profile.get_attributes()
            info_list = [name]
            
            # get attribs
            for value in attrib_dict.values():
                info_list.append(value)
                
            prof_string = ','.join(info_list)
            self._legend_file.write_line(prof_string)

    def _new_profile_directory(self, name:str) -> None:
        '''Creates new folders for the user
        
        Input: str - name
        Return: None'''
        # create directories needed
        cwd = os.getcwd()
        path_1 = os.path.join(cwd,f'profiles/{name}')
        os.mkdir(path_1)
        self._new_profile_db(path_1)   # create db
            
    def _new_profile_db(self, path:str) -> Database:
        '''Creates the database for the new user
        
        Input: str - path
        Return: Database Object'''
        prof_db = Database(f'{path}/{DB_NAME}')
        print(prof_db)
        
        # create all needed tables
        for table in DB_TABLES:
            t_name = table[0]
            t_cols = table[1]
            prof_db.create_table(t_name,t_cols)
        
        return prof_db
        
    def _new_profile_check(self, name:str, attributes:list) -> bool:
        '''Checks to make sure that new profile added does not
        violate any rules. If valid, returns True else False.
        
        Input: None
        Return: bool - valid or no'''
        # attribute # check
        if len(attributes) != len(ATTRIBUTES):
            raise Exception('Error: Invalid amount of attributes given')
        
        # unique name check
        for profile in self._profiles:
            if profile.get_name() == name:
                return False
            
        return True
        
    def __str__(self) -> str:
        '''Prints out currently loaded profile names'''
        display_str = 'Currently loaded profile names: \n\n'
        
        for profile in self._profiles:
            name = profile.get_name()
            display_str += f'{name}\n'
            
        return display_str
        
def main():
    manager = ProfileManager()
    
if __name__ == '__main__':
    main()