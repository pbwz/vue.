'''
University Class class for vue

Author: Paul Belland
'''
import random
from uni_assignment import AE_Object
from quickcrypt import QuickCrypt
TABLE_NAME = 'Classes'
TABLE_IDENT = 'Class_ID'
TABLE_VALS = ['Class_Name','Professor','WGPA']

# AE ID config
UPPER_BOUND = 10000
LOWER_BOUND = 1

class Uni_Class:
    '''Class Object'''
    
    def __init__(self, database, class_ID, passkey) -> None:
        self._db = database
        self._class_ID = class_ID
        self._class_name = None
        self._class_prof = None
        self._semester = None
        self._wanted_gpa = None
        self._AE_objects = []
        self._passkey = passkey
        
        # populate class
        self._read_db()
    
    def add_assign_exam(self, ae_type:str, name:str, 
                        weight:str, date:str, grade:str) -> None:
        '''Creates a new AEObject, adds it to the database and
        also saves a reference to the instance in a list
        
        Input: str, int, str, str, str, str
        Return: None'''
        new_id = self._get_new_id()
        
        # encrypt grade value
        quick = QuickCrypt(self._passkey)
        enc_grade = quick.encrypt(grade)
        
        # add to db and create object
        vals = [self._class_ID,new_id,name,date,weight,ae_type,enc_grade]
        self._db.insert('AE',vals)
        new_object = AE_Object(self._db, new_id, self._passkey)
        self._AE_objects.append(new_object)
        
    def create_AE_objects(self) -> None:
        '''Creates all AEObjects needed to hold exam
        and assignment information.
        
        Input: None
        Return: None'''
        res = self._db.search_for('AE','Class_ID',self._class_ID)
        
        # create and save copy of AE objects to class
        for item in res:
            ae_id = item[1]
            new_ae = AE_Object(self._db, ae_id, self._passkey)
            self._AE_objects.append(new_ae)
    
    def get_class_ID(self) -> int:
        '''Returns ID of class
        
        Input: None
        Return: int'''
        return self._class_ID
    
    def get_name(self) -> str:
        '''Returns name of class
        
        Input: None
        Return: str'''
        return self._class_name
    
    def get_prof(self) -> str:
        '''Returns the name of the professor
        
        Input: None
        Return: str'''
        return self._class_prof
    
    def get_semester(self) -> str:
        '''Returns the semester the class was saved to
        
        Input: None
        Return: str'''
        return self._semester
    
    def get_wgpa(self) -> int:
        '''Returns the wanted GPA for the class
        
        Input: None
        Return: int'''
        return self._wanted_gpa
    
    def set_name(self, name:str) -> None:
        '''Sets the name of the given class
        
        Input: str
        Return: None'''
        if type(name) != str:
            raise ValueError('Expected str')
        self._class_name = name
        
    def set_prof(self, prof:str) -> None:
        '''Sets the name of the professor
        
        Input: str
        Return: None'''
        if type(prof) != str:
            raise ValueError('Expected str')
        self._class_prof = prof
        
    def set_wgpa(self, w_gpa:int) -> None:
        '''Sets the wanted GPA for the class
        
        Input: int
        Return: None'''
        if type(w_gpa) != int:
            raise ValueError('Expected int')
        self._wanted_gpa = w_gpa
   
    def update_db(self) -> None:
        '''Updates the database with the newest info
        
        Input: None
        Return: None'''
        for col in TABLE_VALS:
            if col == 'Class_Name':
                val = self._class_name
            elif col == 'Professor':
                val = self._class_prof
            elif col == 'WGPA':
                val = self._wanted_gpa
            self._db.insert_for(TABLE_NAME,TABLE_IDENT,self._class_ID,col,val)
        
    def _read_db(self) -> None:
        '''Reads all class data from the database
        
        Input: None
        Return: None'''
        row = self._db.search_for(TABLE_NAME,'Class_ID',self._class_ID)
        data = row[0]
        
        self._semester = data[1]
        self._class_name = data[2]
        self._class_prof = data[3]
        self._wanted_gpa = data[4]

    def _get_new_id(self) -> int:
        '''Finds and returns a unique ID for a new class
        
        Input: None
        Returns: int'''
        all_ids = range(LOWER_BOUND,UPPER_BOUND)
        taken_ids = self._db.get_table_col('AE','AE_ID')
        unused_ids = set(all_ids) ^ set(taken_ids)
        
        return random.choice(list(unused_ids))