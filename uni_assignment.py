'''
An assignment/exam object that can be given data. Written
for vue.

Author: Paul Belland
'''

from quickcrypt import QuickCrypt

class AE_Object:
    def __init__(self, database, ae_id, passkey) -> None:
        self._db = database
        self._ae_id = ae_id
        self._name = None
        self._weight = None
        self._date = None
        self._grade = None
        self._ae_type = None
        self._passkey = passkey
        
    def get_name(self) -> str:
        '''Returns assignment/exam name
        
        Input: None
        Return: str'''
        return self._name
    
    def get_weight(self) -> str:
        '''Returns assignment weight
        
        Input: None
        Return: str'''
        return self._weight
    
    def get_date(self) -> str:
        '''Returns assignment due date
        
        Input: None
        Return: str'''
        return self._date
    
    def get_grade(self) -> int:
        '''Returns assignment grade %
        
        Input: None
        Return: int'''
        return self._grade
        
    def _read_db(self) -> None:
        '''Reads data from database, updates AEObject
        
        Input: None
        Return: None'''
        res = self._db.search_for('AE','AE_ID',self._ae_id)
        
        # get indiv items
        data = res[0]
        self._name = data[2]
        self._date = data[3]
        self._weight = data[4]
        enc_grade = data[5]
        
        # decrypt grade
        quick = QuickCrypt(self._passkey)
        self._grade = quick.decrypt(enc_grade)
        