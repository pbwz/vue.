'''
File Helper V1.1

A simple program to speed up my project creation. Handles
reading and writing to files + encryption.

How to use:
- Create an instance of FileHelper as follows:
    + file = FileHelper('name_of_file.txt') | Non Encrypted
    + file = FileHelper('name_of_file.txt', 'passkey', 'optional salt') | Encrypted

Capabilities:
- Read .txt files and return them stripped of any useless data
- Read .csv files and attempt to interpret them
- Read an encrypted .txt file and decipher using a key

- Write .txt files passed in a form
- Write an encrypted .txt file enciphered using AES

Planned:
- .csv support and automatic interpretation

Author: Paul Belland
'''

import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
ALLOWED_TYPES = ('.txt','.csv')

class FileHelper:
    '''Quickly create regular/encrypted files + decrypt'''
    def __init__(self, file_name, passkey = None):
        self.file_name = file_name
        self.passkey = passkey
        self.salt = get_random_bytes(32)
        
        # catch bad file types
        name_len = len(self.file_name)
        file_type = self.file_name[name_len-4:]
        
        if self.passkey:
            self.get_key()
        
        if file_type not in ALLOWED_TYPES:
            raise Exception('FileHelper: File format not supported')
        
        self.file_type = file_type
        
        
    def read_file(self, d_type = 'str') -> list:
        '''Attempts to read file'''
        # check if file exists
        if not self.passkey:
            try:
                with open(self.file_name, 'r') as raw_file:
                    raw_data = raw_file.readlines()
            except FileNotFoundError:
                raise Exception('FileHelper: File not found')
        
            if self.file_type == '.txt':
                    self.format_text(raw_data, d_type)
                    
            return self.formatted
        
        else:
            
            return self.decrypt_data()

            
            
    def write_file(self, data):
        '''Writes file based on parameters'''
        try:
            if self.passkey != None:   # if set, encrypts
                with open(self.file_name, 'wb') as w_file:
                    cipher, enc_data = self.encrypt_data(data)
                    w_file.write(self.salt)
                    w_file.write(cipher.nonce)
                    w_file.write(enc_data)
                    w_file.write(cipher.digest())
            else:   # for non-encrypted
                with open(self.file_name, 'w') as w_file:
                    for line in data:
                        w_file.write(f'{str(line)}\n')
        except:
            raise Exception('FileHelper: Unexpected error, failed to write')
        
        
    def write_line(self, data, new_line = True):
        '''Writes a line to a file'''
        with open(self.file_name, 'a') as w_file:
            if new_line:
                data += '\n'
            w_file.write(data)
    
    def wipe_file(self):
        '''Wipes all data from file'''
        with open(self.file_name, 'w') as w_file:
            pass
            
    def get_key(self):
        '''Uses the salt and password to recreate the needed key'''
        key = PBKDF2(self.passkey, self.salt, dkLen=32)
        self.key = key
        return key
    
    
    def encrypt_data(self, data):
        '''Encrypts using AES'''
        cipher =  AES.new(self.key, AES.MODE_GCM)
        byte_data = bytes(data, 'utf-8')
        ciphered_data = cipher.encrypt(byte_data)
        
        return cipher, ciphered_data
    
    def decrypt_data(self):
        '''Attempts to decrypt file'''
        try:
            size = os.path.getsize(self.file_name)
            enc_file_size = size - 32 - 16 - 16
        except FileNotFoundError:
            raise Exception('FileHelper: That file does not exist')
        
        with open(self.file_name, 'rb') as read_file:
            self.salt = read_file.read(32)
            nonce = read_file.read(16)
            key = self.get_key()
            cipher = AES.new(key, AES.MODE_GCM, nonce = nonce)
            
            data = read_file.read(enc_file_size)
            decrypt_data = cipher.decrypt(data)
            
            tag = read_file.read(16)
            try:
                cipher.verify(tag)
                return str(decrypt_data, 'utf-8')
            except:
                return 'Wrong password/File was tampered with!'
                
                
        
    def format_text(self, raw_data, d_type):
        '''Formats raw text files into useful lists'''
        fmtd_data = []
        
        for line in raw_data:
            fmtd_line = line.strip()
            
            if d_type == 'int':
                fmtd_line = int(fmtd_line)
            
            fmtd_data.append(fmtd_line)
            
        self.formatted = fmtd_data

def main():
    '''Testing purposes'''
    data = 'This message is very important'
    test = FileHelper('test.txt','ABCpassword')
    
    a = test.write_file(data)

if __name__ == '__main__':
    main()