from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from Backend.SpentML import SpentML
from utils.AccountManager import authenticate
from utils.session import set_user
from kivy.utils import platform
from Screens.InsightsScreen import InsightsScreen


class LoginScreen(MDScreen):
    def try_login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        print(f"DEBUG login: username=<{username}>, password=<{password}>")

        if authenticate(username, password):
            set_user(username)
            self.ids.username.text = ''
            self.ids.password.text = ''
            # Get the insights screen from the ScreenManager
            insights_screen = self.manager.get_screen("insights")
            # Update the insights screen with the current username.
            insights_screen.ml_engine = SpentML(username=username)
            # Optionally, if you have a reset() or set_username() method, call that:
            # insights_screen.set_username(username)
            # Switch to the appropriate screen (for desktop "pc", for mobile "phone")
            if platform in ['android', 'ios']:
                self.manager.current = 'phone'
            else:
                self.manager.current = 'pc'
        else:
            self.ids.message.text = '❌ Invalid username or password'

    def go_to_signup(self):
        self.manager.current = 'signup'

