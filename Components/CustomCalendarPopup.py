import calendar
import datetime
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.metrics import dp

class CustomCalendarPopup(Popup):
    def __init__(self, callback, **kwargs):
        super(CustomCalendarPopup, self).__init__(**kwargs)
        self.callback = callback
        self.title = "Select a Date"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

        # Use current year and month by default
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month

        # Build the calendar grid
        self.content = self.build_calendar()

    def build_calendar(self):
        grid = GridLayout(cols=7, spacing=dp(5), padding=dp(10))
        # Add weekday headers
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            header = Button(text=day, size_hint=(None, None), size=(dp(40), dp(40)),
                            background_color=(0.8, 0.8, 0.8, 1), disabled=True)
            grid.add_widget(header)

        # Get a matrix for the month (weeks as lists of ints, with 0 for days not in the month)
        month_matrix = calendar.monthcalendar(self.year, self.month)
        for week in month_matrix:
            for day in week:
                if day == 0:
                    grid.add_widget(Button(text="", size_hint=(None, None), size=(dp(40), dp(40)), disabled=True))
                else:
                    btn = Button(text=str(day), size_hint=(None, None), size=(dp(40), dp(40)))
                    # Bind a lambda that passes the chosen day (capture day with default argument)
                    btn.bind(on_release=lambda inst, d=day: self.select_date(d))
                    grid.add_widget(btn)
        return grid

    def select_date(self, day):
        # Build date string from year, month, day and call the callback
        selected_date = datetime.date(self.year, self.month, day)
        self.callback(selected_date)
        self.dismiss()
