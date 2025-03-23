from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.clock import Clock

from Components.MenuBar import MenuBar

class InsightsScreen(MDScreen):
    def __init__(self, **kwargs):
        super(InsightsScreen, self).__init__(**kwargs)

        # Main container for spacing/padding
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Content layout (holds labels/buttons)
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Title label (no emoji)
        self.title_label = MDLabel(
            text="Transaction Categorization & Insights",
            font_style="H5",
            halign="center"
        )

        # Info label
        self.info_label = MDLabel(
            text="Categorized transactions, insights, and graphs go here.",
            font_style="Body1",
            halign="center"
        )

        # Button to Forecast
        self.btn_to_forecast = MDRaisedButton(
            text="Go to Forecasting",
            size_hint=(None, None),
            width=dp(180),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_forecasting
        )

        # Add them to the content layout
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.info_label)
        self.layout.add_widget(self.btn_to_forecast)

        # Put the content layout into the root_layout
        self.root_layout.add_widget(self.layout)

        # Finally, add root_layout to the screen
        self.add_widget(self.root_layout)

        # Insert the menu bar once KV is loaded
        Clock.schedule_once(self.add_menu_bar, 0)

    def add_menu_bar(self, dt):
        # Insert the MenuBar at the top
        menu = MenuBar(screen_manager=self.manager)
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(menu)
        self.root_layout.add_widget(self.layout)

    def go_to_forecasting(self, instance):
        self.manager.current = 'forecast'
