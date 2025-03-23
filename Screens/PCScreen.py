from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.clock import Clock

from Components.MenuBar import MenuBar
from utils.session import get_user

class PCScreen(MDScreen):
    def __init__(self, **kwargs):
        super(PCScreen, self).__init__(**kwargs)

        # --------------------------
        #  MAIN LAYOUT + STYLE
        # --------------------------
        # A top-level layout with some padding, spacing
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # We'll hold our actual screen content in a second layout
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # 1) Welcome label
        self.welcome_label = MDLabel(
            text=f"Welcome, {get_user()} 👋",
            font_style="H5",     # nice readable size
            halign="center"
        )

        # 2) Placeholder label
        self.placeholder_label = MDLabel(
            text="This is the PC UI Placeholder",
            font_style="H5",
            halign="center"
        )

        # 3) Logout button
        self.logout_btn = MDRaisedButton(
            text="Logout",
            size_hint=(None, None),
            width=dp(120),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            on_release=self.logout
        )

        # Add these widgets to our content layout
        self.layout.add_widget(self.welcome_label)
        self.layout.add_widget(self.placeholder_label)
        self.layout.add_widget(self.logout_btn)

        # Finally, add the content layout to the root_layout
        self.root_layout.add_widget(self.layout)

        # Add the root_layout to the screen
        self.add_widget(self.root_layout)

        # We'll dynamically insert the MenuBar once the .kv is loaded
        Clock.schedule_once(self.add_menu_bar, 0)

    def add_menu_bar(self, dt):
        menu = MenuBar(screen_manager=self.manager)

        # Replace everything in root_layout with [MenuBar, self.layout]
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(menu)
        self.root_layout.add_widget(self.layout)

    def on_pre_enter(self):
        # Update welcome label to show the current user
        self.welcome_label.text = f"Welcome, {get_user()}"

    def logout(self, instance):
        self.manager.current = 'login'
