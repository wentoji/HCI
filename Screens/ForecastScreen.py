from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.clock import Clock

from Components.MenuBar import MenuBar

class ForecastScreen(MDScreen):
    def __init__(self, **kwargs):
        super(ForecastScreen, self).__init__(**kwargs)

        # Main container: spacing/padding
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Inner layout for content
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Title label
        self.title_label = MDLabel(
            text="Budget Forecast & Recommendations",
            font_style="H5",
            halign="center"
        )

        # Info label
        self.info_label = MDLabel(
            text="Forecasted budget, recommendations, and goal tracking here.",
            font_style="Body1",
            halign="center"
        )

        # Button to go to Insights
        self.btn_to_insights = MDRaisedButton(
            text="Go to Insights",
            size_hint=(None, None),
            width=dp(150),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_insights
        )

        # Add them to layout
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.info_label)
        self.layout.add_widget(self.btn_to_insights)

        # Put layout into root_layout
        self.root_layout.add_widget(self.layout)

        # Add root_layout to the screen
        self.add_widget(self.root_layout)

        # Schedule insertion of menu bar after KV loads
        Clock.schedule_once(self.add_menu_bar, 0)

    def add_menu_bar(self, dt):
        # Insert the MDDropdownMenu-based MenuBar
        menu = MenuBar(screen_manager=self.manager)
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(menu)
        self.root_layout.add_widget(self.layout)

    def go_to_insights(self, instance):
        self.manager.current = 'insights'
