from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.clock import Clock

from Components.MenuBar import MenuBar
from utils.session import get_user

class PhoneScreen(MDScreen):
    def __init__(self, **kwargs):
        super(PhoneScreen, self).__init__(**kwargs)

        # A top-level layout with spacing/padding
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Content layout where we'll hold labels/buttons
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Welcome label (no emojis)
        self.welcome_label = MDLabel(
            text=f"Welcome, {get_user()}",
            font_style="H5",
            halign="center"
        )

        # Placeholder label (no phone emoji)
        self.placeholder_label = MDLabel(
            text="This is the Phone UI Placeholder",
            font_style="H5",
            halign="center"
        )

        # Logout button
        self.logout_btn = MDRaisedButton(
            text="Logout",
            size_hint=(None, None),
            width=dp(100),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            on_release=self.logout
        )

        # Add widgets to content layout
        self.layout.add_widget(self.welcome_label)
        self.layout.add_widget(self.placeholder_label)
        self.layout.add_widget(self.logout_btn)

        # Add content layout to the root layout
        self.root_layout.add_widget(self.layout)

        # Add root layout to the screen
        self.add_widget(self.root_layout)

        # Schedule the menu bar insertion after KV loads
        Clock.schedule_once(self.add_menu_bar, 0)

    def add_menu_bar(self, dt):
        # Insert the MenuBar at the top, then the rest of the content
        menu = MenuBar(screen_manager=self.manager)
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(menu)
        self.root_layout.add_widget(self.layout)

    def on_pre_enter(self):
        # Update welcome text in case user changed
        self.welcome_label.text = f"Welcome, {get_user()}"

    def logout(self, instance):
        self.manager.current = 'login'
