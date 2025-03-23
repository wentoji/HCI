from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivy.metrics import dp


class MenuBar(MDBoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        # Make the menubar span the full width at the top
        self.size_hint = (1, None)
        self.height = dp(56)
        self.orientation = 'horizontal'
        self.padding = dp(10)  # small left/right padding
        self.screen_manager = screen_manager

        # MDDropdownMenu items
        self.menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Home",
                "height": dp(48),
                "on_release": lambda x="pc": self.select_screen(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Insights",
                "height": dp(48),
                "on_release": lambda x="insights": self.select_screen(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Forecast",
                "height": dp(48),
                "on_release": lambda x="forecast": self.select_screen(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Settings",
                "height": dp(48),
                "on_release": lambda x="settings": self.select_screen(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Logout",
                "height": dp(48),
                "on_release": lambda x="login": self.select_screen(x)
            }
        ]

        # Create the actual MDDropdownMenu
        self.menu = MDDropdownMenu(
            caller=None,         # We'll set the caller below
            items=self.menu_items,
            width=dp(200)
        )

        # Icon button to open the dropdown
        self.main_button = MDIconButton(
            icon="menu",
            pos_hint={"center_y": 0.5}
        )
        # Fix the extra arg error by using a lambda with *args:
        self.main_button.bind(on_release=lambda *args: self.open_menu())

        self.add_widget(self.main_button)

    def open_menu(self):
        """Open the MDDropdownMenu anchored to the icon button."""
        self.menu.caller = self.main_button  # anchor to this button
        self.menu.open()

    def select_screen(self, screen_name):
        """Switch screens, then close the menu."""
        self.screen_manager.current = screen_name
        self.menu.dismiss()
