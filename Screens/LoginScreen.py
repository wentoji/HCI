from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from utils.AccountManager import authenticate
from utils.session import set_user
from kivy.utils import platform

class LoginScreen(MDScreen):
    def try_login(self):

        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        print(f"DEBUG login: username=<{username}>, password=<{password}>")

        if authenticate(username, password):
            set_user(username)
            self.ids.username.text = ''
            self.ids.password.text = ''
            if platform in ['android', 'ios']:
                self.manager.current = 'phone'
            else:
                self.manager.current = 'pc'
        else:
            self.ids.message.text = '❌ Invalid username or password'

    def go_to_signup(self):
        self.manager.current = 'signup'

