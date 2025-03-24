from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

# Import all screens except Onboarding, which is in pure Python
from Screens.LoginScreen import LoginScreen
from Screens.SignupScreen import SignupScreen
from Screens.PhoneScreen import PhoneScreen
from Screens.PCScreen import PCScreen
from Screens.InsightsScreen import InsightsScreen
from Screens.ForecastScreen import ForecastScreen
from Screens.SettingsScreen import SettingsScreen
from Screens.OnboardingScreen import OnboardingScreen

class MainApp(MDApp):
    def build(self):
        # Load the single .kv file
        Builder.load_file("all_screens.kv")

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(PhoneScreen(name='phone'))
        sm.add_widget(PCScreen(name='pc'))
        sm.add_widget(InsightsScreen(name='insights'))
        sm.add_widget(ForecastScreen(name='forecast'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(OnboardingScreen(name='onboarding'))

        sm.current = "login"
        return sm

if __name__ == '__main__':
    MainApp().run()
