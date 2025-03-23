from kivymd.uix.screen import MDScreen
from utils.AccountManager import create_account
from utils.session import set_user


class SignupScreen(MDScreen):
    def try_signup(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        if create_account(username, password):
            set_user(username)

            # Clear fields
            self.ids.username.text = ''
            self.ids.password.text = ''

            self.ids.message.text = '✅ Account created! Proceed to onboarding.'
            self.manager.current = 'onboarding'
        else:
            self.ids.message.text = '⚠️ Username already exists'

    def go_to_login(self):
        self.manager.current = 'login'
