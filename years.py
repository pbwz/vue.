'''
A simple script to create year pairs.
Intended for use with vue, to create
school year pairs.

Author: Paul Belland
'''
# DO NOT CHANGE
POS_FORMATS = ('YY','YYYY')

# configurations
START = 2020
END = 2030
YEAR_SEM_SPACER = ' '
SEMESTER_OPTIONS = ('Fall','Winter')

# formatting
SEPARATOR = '/'
CHOSEN_FORMAT = 0

def get_year_list():
    '''Creates and returns a list containing year pair strings'''
    first_vals = range(START, END+1)
    second_vals = range(START+1, END+2)
    pair_list = []
    yr_format = len(POS_FORMATS[CHOSEN_FORMAT])
    
    for i in range(len(first_vals)):
        pair_str = ''
        pair_str += str(first_vals[i])[-yr_format:]
        pair_str += SEPARATOR
        pair_str += str(second_vals[i])[-yr_format:]
        
        pair_list.append(pair_str)
        
    return pair_list

def get_sem_list():
    '''Creates and returns a list containing year pair strings
    appended with an F or W for Fall and Winter'''
    sem_list = []
    
    # build sem list
    for semester in SEMESTER_OPTIONS:
        for year_pair in get_year_list():
            sem = year_pair + YEAR_SEM_SPACER + semester
            sem_list.append(sem)
            
    return sem_list
    
def main():
    print(get_sem_list())
    
if __name__ == '__main__':
    main()