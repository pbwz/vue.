'''
vue.

University class planner, scheduler and grade tracker

Author: Paul Belland
'''

# module imports
from vue_man import ProfileManager
from years import get_year_list
import random

# WINDOW CONFIG *MUST BE AT BEGINNING*
from kivy import Config
Config.set('graphics', 'width', '1250')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'minimum_width', '1250')
Config.set('graphics', 'minimum_height', '700')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

# kivy ui imports
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivy.app import App

# temp for testing
GEN_NAME = 'Paul'
GEN_GPA = '3.74'
GEN_CLASS = 'BIOL 322'
ICONS = ('dog','tools','github')
GEN_SEMESTER = '23/24 Fall'

# KV Widget Classes
class Content(BoxLayout):
    '''Content for profile creation'''

class ClassContent(BoxLayout):
    '''Content for class creation'''

class AEContent(BoxLayout):
    '''Content for assignment/exam creation'''
    def on_save(self, instance, value, date_range):
        '''
        Events called when the "OK" dialog box button is clicked.

        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        '''

        print(instance, value, date_range)

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

class ClassCard(MDCard):
    '''Clickable card widget for displaying classes'''

class BlankCard(MDCard):
    '''Non-clickable card widget representing empty class'''
    
class MenuHeader(MDBoxLayout):
    '''Dropdown menu header for years selector in settings'''

class CircularProgressBar(AnchorLayout):
    '''Circlular progress bar for home page'''
    bar_color = ListProperty([1,0,100/255])
    bar_width = NumericProperty(10)
    progress = NumericProperty(1)
    
# Screen Classes
class MindBlockScreen(Screen):
    '''MindBlock Screen Class'''
    
    def on_enter(self, *args):
        pass
        
    def add_new(self):
        print('Add new')
        
    def open_note(self):
        print('Opening New')
        
class NavBarScreen(Screen):
    '''NavigationBar Screen Class'''
    
    def on_kv_post(self, base_widget):
        '''Save nav logout button to app so we can
        access it later on from different manager'''
        app = App.get_running_app()
        app.nbtn_logout = self.ids.nbtn_logout
        app.nav_manager = self.manager
        self.ids.nbtn_logout.on_release = self.manager.get_screen('sc_login').logout
    
    def on_pre_enter(self):
        '''
        Set profile and prof_manager across all screens
        '''
        if self.ids:  # stop premature firing
            self.ids.sc_manager.current = 'sc_home'
            
            # get login screen info
            prof_man = self.manager.get_screen('sc_login').prof_man
            profile = self.manager.get_screen('sc_login').profile
            
            # apply to all screens
            for screen in ('sc_home','sc_settings','sc_analytics','sc_class'):
                self.ids.sc_manager.get_screen(screen).profile = profile
                self.ids.sc_manager.get_screen(screen).prof_man = prof_man
                
            # initial homescreen setup workaround
            self.ids.sc_manager.get_screen('sc_home').personalize()

class LoginScreen(Screen):
    '''Login Screen Class'''
    
    def on_kv_post(self, base_widget):
        '''
        Basic login screen setup for first start
        '''
        self.anim_in_prog = False   # button anim inactive
        self.dialog = False
        self.prof_man = ProfileManager()
        self.list_profiles()
        self.selected_prof = None
        self.current_not = None
        self.active_name = None
        self.select_profile(self.prof_man.get_preferred())
        Clock.schedule_once(self.focus_pass, 0.5)
        
    def logout(self):
        '''
        Handles logout functions 
        '''
        self.manager.current = 'sc_login'
        self.ids.txtf_password.text = ''
        self.profile.logout()
        self.profile = None
        self.active_name = None
    
    def focus_pass(self, dt):
        '''
        Focuses password input box
        '''
        self.ids.txtf_password.focus = True
    
    def new_prof_dialog(self):
        '''
        Dialog creation for new profile creation
        '''
        if not self.dialog:   # ensure no dialog is present
            
            # styling
            self.dialog = MDDialog(
                title="New Profile",
                type="custom",
                md_bg_color='#263238',
                content_cls=Content(),
                buttons=[
                    MDRaisedButton(
                        text="CREATE",
                        md_bg_color='orange',
                        theme_text_color="Custom",
                        on_press=self.new_validate,
                    ),
                ],
            )
            
        self.dialog.open()
        
    def new_validate(self, widget):
        '''
        Called upon validation of new profile
        '''
        # get inputs from dialog
        name = self.dialog.content_cls.ids.txtf_new_prof.text
        password = self.dialog.content_cls.ids.txtf_new_pass.text
        
        # check if name input is valid
        if not name:
            self.dialog.title = 'Enter a name!'
            Clock.schedule_once(self.reset_prof_dialog, 1)
            
        # check if password input is valid
        elif not self.validate_password(password):
            self.dialog.title = 'No password entered!'
            Clock.schedule_once(self.reset_prof_dialog, 1)
            
        # passed checks
        else:
            response = self.create_profile(name, password)
            self.dialog.title = response
            Clock.schedule_once(self.reset_prof_dialog, 0.5)
                
    def validate_password(self, password):
        '''
        Checks if password meets requirements
        '''
        if password:
            return True
            
    def reset_prof_dialog(self, dt):
        '''
        Resets profile creation text box
        
        TODO Split success and new profile reset methods
        '''
        if dt < 0.8:  # created succesfully
            self.dialog.dismiss(force=True)
        else:   # failed a check
            self.dialog.title = 'New Profile'
    
    def create_profile(self, name, password):
        '''
        Attempts to create new profile
        '''
        rand_icon = random.choice(ICONS)
        response = self.prof_man.new_profile(name,password,[rand_icon,GEN_SEMESTER])
        
        if response[0] == 'C': # created successfully
            self.dialog.content_cls.ids.txtf_new_prof.text = ''
            self.dialog.content_cls.ids.txtf_new_pass.text = ''
            
        self.list_profiles()   # reflect creation login list
        return response
    
    def notification_box(self,text):
        '''
        Small textbox notification logic
        '''
        if not self.current_not:  # ensures no notification present
            
            # style
            self.current_not = Snackbar(
                text=text,
                radius=[10,10,10,10],
                snackbar_x="500dp",
                snackbar_y="30dp",
                )
            self.current_not.size_hint_x = (
                self.width - (self.current_not.snackbar_x * 2)
            ) / self.width
            
            # display notification
            self.current_not.open()
            Clock.schedule_once(self.dismiss_notification, 1)
        
    def dismiss_notification(self, dt):
        '''
        Dismisses notification box
        '''
        if self.current_not:
            self.current_not.dismiss()
            self.current_not = None
        
    def login(self):
        '''
        Called when user presses the login button
        '''
        # check if pwd is valid
        if self.validate_pass():  # good
            self.manager.current = 'sc_nav'
            self.active_name = self.profile.get_name()
        else:   # bad
            self.ids.btn_sign_in.text = 'Incorrect'
            self.anim_in_prog = True
            Clock.schedule_once(self.reset_anim_login, 1)
    
    def reset_anim_login(self, dt):
        '''
        Changes the profile text back to normal
        '''
        self.ids.btn_sign_in.text = 'Sign In'
        self.anim_in_prog = False
        
    def select_profile(self, num):
        '''
        Detects which profile is selected
        '''
        if num == 0:  # nothing selected
            self.ids.txt_prof.text = 'Select a profile'
        else:   # selected
            if self.selected_prof == num:
                response = self.prof_man.set_preferred(num)
                self.notification_box(response)
                
            # save choice and display
            self.selected_prof = num
            self.ids.txt_prof.text = f'Profile {num} selected'
        
    def validate_pass(self):
        '''
        Sends txtf_password to profile and then returns
        status of login
        '''
        self.profile = self.prof_man.get_all_profiles()[self.selected_prof-1]  # retrieve profile
        self.profile.try_password(self.ids.txtf_password.text)  # send pwd to profile
        return self.profile.get_login_status()  # get login status
        
    def list_profiles(self):
        '''
        Using data from vue_manager, lists all created
        profiles and icons on the login page
        '''
        prof_list = self.prof_man.get_all_profiles()
        
        # iterate through list, display
        for i in range(len(prof_list)):
            name = prof_list[i].get_name()
            icon = prof_list[i].get_attribute('icon')
            
            dyn_name = f'list_{i+1}'
            dyn_icon = f'licon_{i+1}'
            
            self.ids[dyn_name].text = name
            self.ids[dyn_icon].icon = icon
            
class HomeScreen(Screen):
    '''Home Screen Class'''
    
    def on_kv_post(self, base_widget):
        '''
        Initial setup
        '''
        self.dialog = None
        
    def on_pre_enter(self):
        '''
        Personalizes home screen with all profile info.
        Called each time entered to keep up to date.
        '''
        app = App.get_running_app()
        
        if self.ids:
            self.personalize()
            app.nbtn_logout.icon = 'account-lock'
            app.nbtn_logout.on_release = app.nav_manager.get_screen('sc_login').logout
            
    def personalize(self):
        '''
        Makes page personalized to profile info
        '''
        # retrieve data
        name = self.profile.get_name()
        semester = self.profile.get_attribute('semester')
        
        # display to screen
        self.ids.txt_welcome.text = f'Welcome back, {name}'
        self.ids.txt_class_sem.text = f'Classes - {semester}'
        self.display_classes()
        
    def display_classes(self):
        '''
        Displays all classes saved for current user
        in current semester
        '''
        # retrieve data
        semester = self.profile.get_attribute('semester')
        classes = self.profile.get_classes(semester)
        blank_amt = 6 - len(classes)
        
        self.ids.grid_classes.clear_widgets()  # remove all old
        
        # display class cards
        for uni_class in classes:
            name = uni_class.get_name()
            gpa = uni_class.get_wgpa()   # CHANGE
            
            card = ClassCard()
            card.on_release = lambda x=uni_class: self.class_screen(x)
            card.ids.txt_class_name.text = name
            card.ids.txt_class_gpa.text = gpa
            
            self.ids.grid_classes.add_widget(card)
            
        # fill in blank spaces
        for i in range(blank_amt):
            blank = BlankCard()
            self.ids.grid_classes.add_widget(blank)
            
    def class_screen(self, uni_class):
        '''Brings user to class screen and sets it up for
        class card that was clicked'''
        self.manager.get_screen('sc_class').current_class = uni_class
        self.manager.current = 'sc_class'
        
    def new_class_dialog(self):
        '''
        Opens the dialog for new class creation
        '''
        if not self.dialog:  # check if dialog exists
            
            # style
            self.dialog = MDDialog(
                title="Add a new class",
                type="custom",
                md_bg_color='#263238',
                content_cls=ClassContent(),
                buttons=[
                    MDRaisedButton(
                        text="CREATE",
                        md_bg_color='orange',
                        theme_text_color="Custom",
                        on_press=self.new_class_validate,
                    ),
                ],
            )
            
        self.dialog.open()
        
    def new_class_validate(self, widget):
        '''
        Validates all fields entered to create new class
        '''
        # retrieve data
        name = self.dialog.content_cls.ids.txtf_class_name.text
        prof = self.dialog.content_cls.ids.txtf_prof_name.text
        gpa = self.dialog.content_cls.ids.txtf_gpa_val.text
        
        # validate
        if not name or not prof or not gpa:  # check if all fields entered
            self.dialog.title = 'Please fill all fields'
            Clock.schedule_once(self.reset_class_dialog, 1)
            
        else: # check GPA value
            try:  
                float(gpa)
            except ValueError:
                self.dialog.title = 'Enter a real number'
                Clock.schedule_once(self.reset_class_dialog, 1)
                
            else:  # all good
                self.new_class_create(name, prof, gpa)
                for item in ('txtf_class_name','txtf_prof_name', 'txtf_gpa_val'):
                    self.dialog.content_cls.ids[item].text = ''
                self.dialog.dismiss(force = True)
                
    def new_class_create(self, name, prof, gpa):
        '''
        After dialog has been validated, creates the class in
        the system
        '''
        semester = self.profile.get_attribute('semester')
        self.profile.add_class(semester, name, prof, gpa)
        self.display_classes()
        
class ClassScreen(Screen):
    '''Class Screen Class'''
    
    def on_pre_enter(self):
        '''
        Populates the screen with correct class information
        '''
        app = App.get_running_app()
        
        if self.ids:  # safety for preloading
            self.populate()
            self.dialog = None
            app.nbtn_logout.icon = 'arrow-left'
            app.nbtn_logout.on_release = self.go_back
            
    def reset_class_dialog(self, dt):
        '''
        Resets the title in the class dialog after an error
        '''
        self.dialog.title = f'Add a new {self.new_type}'
            
    def add_new_dialog(self, ae_type):
        '''
        Opens the dialog for new exam/assign creation
        '''
        self.new_type = ae_type
        if not self.dialog:
            
            # style
            self.dialog = MDDialog(
                title=f"Add a new {ae_type}",
                type="custom",
                md_bg_color='#263238',
                content_cls=AEContent(),
                buttons=[
                    MDRaisedButton(
                        text="CREATE",
                        md_bg_color='orange',
                        theme_text_color="Custom",
                        on_press=self.add_new_validate,
                    ),
                ],
            )
            
        self.dialog.open()
            
    def add_new_validate(self, widget):
        '''
        Validation for adding new assign/exam
        '''
        # retrieve data
        name = self.dialog.content_cls.ids.txtf_name.text
        weight = self.dialog.content_cls.ids.txtf_weight.text
        date = self.dialog.content_cls.ids.txtf_date.text
        
        # validate
        if not name or not weight:
            self.dialog.title = 'Please name and weight fields'
            Clock.schedule_once(self.reset_class_dialog, 1)
        else:
            
            # validate float value
            try:  
                float(weight)
            except ValueError:
                self.dialog.title = 'Enter a real number'
                Clock.schedule_once(self.reset_class_dialog, 1)
                
            else:  # passed, create
                self.add_new(self.new_type, name, weight, date)
                for item in ('txtf_name','txtf_weight', 'txtf_date'):
                    self.dialog.content_cls.ids[item].text = ''
                self.dialog.dismiss(force = True)
            
    def add_new(self, ae_type, name, weight, date):
        '''
        Handles backend interaction to add new class
        to system and storage
        '''
        if date == '':
            date = None
        grade = '100'
        
        self.current_class.add_assign_exam(ae_type, name, weight, date, grade)
            
    def populate(self):
        '''
        Populates the page with the correct class information
        '''
        spacer = '   - '
        
        # retrieve data
        name = self.current_class.get_name()
        prof = self.current_class.get_prof()
        w_gpa = self.current_class.get_wgpa()
        
        # display data
        self.ids.txt_class_name.text = name
        self.ids.txt_class_prof.text = f'{spacer}Professor {prof}'
        self.ids.txt_class_wgpa.text = f'{spacer}Your GPA goal is: {w_gpa}'
    
    def go_back(self):
        '''
        When called, returns user to home screen
        '''
        self.manager.current = 'sc_home'
        
    def remove_class(self, widget):
        '''Removes class from the database, updates screen
        
        Input: class
        Return: None'''
        self.profile.remove_class(self.current_class)
        self.current_class = None
        self.go_back(None)
    
    def class_settings(self):
        print('yep settings')

class AnalyticsScreen(Screen):
    '''Analytics Screen Class'''

class SettingsScreen(Screen):
    '''Settings Screen Class'''
    
    def on_pre_enter(self):
        '''
        Called each time to ensure all data is up to date
        '''
        self.semester = self.profile.get_attribute('semester')
        self.year_pairs = get_year_list()
        self.year = self.semester[0:5]
        self.season = self.semester[6:]
        self.ids.btn_year.text = self.year
        self.update_sem_info()
        
    def set_icon(self, icon):
        '''
        Allows user to change their profile icon
        '''
        self.profile.add_attribute('icon',icon)
        self.prof_man._write_legend()
        
    def year_menu_open(self):
        '''
        Opens the year selection dropdown
        '''
        # get items for menu
        menu_items = [
            {
                "text": f"{year_pair}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{year_pair}": self.set_year(x),
            } for year_pair in self.year_pairs
        ]
        
        # style menu
        self.dropdown = MDDropdownMenu(
            header_cls=MenuHeader(),
            caller=self.ids.btn_year, items=menu_items, width_mult=2, max_height=dp(300),
        )
        
        self.dropdown.open()
        
    def update_sem_info(self):
        '''
        Updates the semester info with the newest data
        '''
        if self.year and self.season:   # only used if
            self.semester = f'{self.year} {self.season}'
        self.profile.add_attribute('semester',self.semester)
        self.prof_man._write_legend()
        self.ids.txt_sem.text = self.semester
        
    def set_year(self, year):
        '''
        Callback for year selection
        '''
        self.year = year
        self.ids.btn_year.text = year
        self.dropdown.dismiss()
        self.update_sem_info()
        
    def set_season(self, season):
        '''
        Sets the semester to whatever is currently selected
        '''
        self.season = season
        self.update_sem_info()
        
# Main App
class VueApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.material_style = 'M3'
        self.root = Builder.load_file('vue_kv.kv')
        return self.root
 
if __name__ == '__main__':
    VueApp().run()