from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.clock import Clock

from Components.MenuBar import MenuBar

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        # Outer layout
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Content layout
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        self.title_label = MDLabel(
            text="Settings & Customization",
            font_style="H5",
            halign="center"
        )
        self.info_label = MDLabel(
            text="Adjust your preferences, manage data, and review account settings.",
            font_style="Body1",
            halign="center"
        )

        self.change_pass_btn = MDRaisedButton(
            text="Change Password (Coming Soon)",
            size_hint=(1, None),
            height=dp(48)
        )
        self.manage_categories_btn = MDRaisedButton(
            text="Manage Categories (Coming Soon)",
            size_hint=(1, None),
            height=dp(48)
        )
        self.clear_data_btn = MDRaisedButton(
            text="Clear Data (Coming Soon)",
            size_hint=(1, None),
            height=dp(48)
        )

        # Add to layout
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.info_label)
        self.layout.add_widget(self.change_pass_btn)
        self.layout.add_widget(self.manage_categories_btn)
        self.layout.add_widget(self.clear_data_btn)

        self.root_layout.add_widget(self.layout)
        self.add_widget(self.root_layout)

        # Insert MenuBar after KV loads
        Clock.schedule_once(self.add_menu_bar, 0)

    def add_menu_bar(self, dt):
        menu = MenuBar(screen_manager=self.manager)
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(menu)
        self.root_layout.add_widget(self.layout)
