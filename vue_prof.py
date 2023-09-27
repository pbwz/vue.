'''
New Profile Class for vue using database and grade matching
to AEDs over the FileHelper method.

Author: Paul Belland
'''

from uni_class import Uni_Class
from years import get_sem_list
from file_helper import FileHelper
import random
MAIN_PATH = './profiles'
LOGIN_FILE = 'login.txt'

# Class ID config
UPPER_BOUND = 1000
LOWER_BOUND = 1

class Profile:
    '''Profile Class for vue.'''
    def __init__(self, name, database) -> None:
        self._name = name
        self._db = database
        self._passkey = None
        self._logged_in = False
        self._attributes = {}
        self._sem_dict = {}

    def get_name(self) -> str:
        '''Returns the name of the Profile
        
        Input: None
        Returns: str'''
        return self._name

    def get_classes(self, semester:str) -> Uni_Class:
        '''Returns list of all classes in the given semester
        Input: str - semester
        Return: list[Uni_Class]'''
        classes = self._sem_dict[semester]
        return classes

    def get_login_status(self) -> bool:
        '''Returns login status
        
        Input: None
        Return: bool - logged in?'''
        return self._logged_in

    def get_attributes(self) -> list:
        '''Returns list of all profile attributes
        
        Input: None
        Return: list'''
        return self._attributes

    def initialize_login_file(self, key:str) -> None:
        '''Writes a blank string to the grade file to handle
        future logins. Should only be called once.'''
        l_file = FileHelper(f'{MAIN_PATH}/{self._name}/{LOGIN_FILE}', key)
        l_file.write_file('')

    def get_attribute(self, attrib_id:str) -> int or str:
        '''Return individual attribute given an identifier
        
        Input: str - identifier name
        Return: int or str - identifier value'''
        if attrib_id in self._attributes.keys():
            return self._attributes[attrib_id]
        else:
            return None

    def add_attribute(self, attrib_id:str, attrib_val:int or str) -> None:
        '''Adds an attribute to the profile
        
        Input: attrib_id - name of attrib, attrib_val - value of attrib
        Return: None'''
        self._attributes[f'{attrib_id}'] = attrib_val

    def try_password(self, key:str) -> bool:
        '''Called when trying passwords. If valid, logs in and
        saves key
        
        Input: None
        Return: bool - login successful?'''
        l_file = FileHelper(f'{MAIN_PATH}/{self._name}/{LOGIN_FILE}', key)
        data = l_file.read_file()
        if data == 'Wrong password/File was tampered with!':
            return False
        else:
            self._logged_in = True
            self._passkey = key
            self._good_login()
            return True 

    def add_class(self,sem:str,name:str,prof:str,w_gpa:float) -> None:
        '''Adds a new class to the database then creates the object
        and stores it in it's respective sem dict.
        
        Input: str - sem, str - name, str - prof, float - w_gpa
        Return: None'''
        new_id = self._get_new_id()
        self._db.insert('Classes',[new_id,sem,name,prof,w_gpa])
        
        # create instance, save to sem dict
        new_class = Uni_Class(self._db, new_id, self._passkey)
        self._sem_dict[sem].append(new_class)
        
    def remove_class(self, uni_class:Uni_Class) -> None:
        '''Removes class from database. Calls Uni_Class remove
        to remove all assignments and exams associated with it.
        
        TODO ASSIGN REMOVAL MUST BE ADDED STILL
        
        Input: int
        Return: None'''
        sem = uni_class.get_semester()
        class_ID = uni_class.get_class_ID()
        
        # remove object
        self._db.delete('Classes','Class_ID',class_ID)
        self._db.delete('AE','Class_ID',class_ID)
        self._sem_dict[sem].remove(uni_class)
        
    def logout(self) -> None:
        '''Called when user logs out of profile,
        wipes all relevant info and sets profile
        back to awaiting login state
        
        Input: None
        Return: None'''
        self._logged_in = False
        self._sem_dict = {}
        
    def _get_new_id(self) -> int:
        '''Finds and returns a unique ID for a new class
        
        Input: None
        Returns: int'''
        all_ids = range(LOWER_BOUND,UPPER_BOUND)
        taken_ids = self._db.get_table_col('Classes','Class_ID')
        unused_ids = set(all_ids) ^ set(taken_ids)
        
        return random.choice(list(unused_ids))

    def _read_classes(self) -> None:
        '''Reads all created classes and ids, updates the dictionary
        
        Input: None
        Return: None'''
        db = self._db
        
        # get classes per sem from db
        for sem in self._sem_dict.keys():
            sem_classes = db.search_for('Classes','Semester',sem)
            
            # get and build indiv classes
            for sem_class in sem_classes:
                c_id = sem_class[0]
                uni_class = Uni_Class(db, c_id, self._passkey)
                self._sem_dict[sem].append(uni_class)

    def _build_sem_dict(self) -> None:
        '''Creates a dictionary using year pairs as keys, to hold all classes
        
        Input: None
        Return: None'''
        self._sem_dict = {}
        
        for semester in get_sem_list():
            self._sem_dict[semester] = []
    
    def _good_login(self) -> None:
        '''Builds rest of profile once logged in successfully
        
        Input: None
        Return: None'''
        self._build_sem_dict()
        self._read_classes()