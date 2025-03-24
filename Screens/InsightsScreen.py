from kivy.uix.image import Image
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
import json
import os

# Use the custom calendar popup instead of MDDatePicker
from Components.CustomCalendarPopup import CustomCalendarPopup

# For the charts (graph size updated in ChartUtils)
from utils.ChartUtils import create_category_bar, create_category_pie

# Our ML backend – note we pass a username here for user-specific data.
from Backend.SpentML import SpentML

from Components.MenuBar import MenuBar


# Helper function to load users (which may include recurring subscriptions and recurring income)
def load_users():
    USERS_FILE = 'users.json'
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)


class InsightsScreen(MDScreen):
    def reset(self):
        """
        Clear UI elements and reinitialize the ML engine (with username cleared).
        Call this on logout.
        """
        self.date_str = ""
        self.date_btn.text = "Pick Date"
        self.desc_input.text = ""
        self.amt_input.text = ""
        self.income_source_input.text = ""
        self.income_amount_input.text = ""
        self.status_label.text = ""
        self.corr_desc_input.text = ""
        self.corr_cat_input.text = ""
        self.corr_status_label.text = ""
        self.m1_input.text = ""
        self.m2_input.text = ""
        self.compare_label.text = ""
        self.chart_box.clear_widgets()
        self.chart_month_input.text = ""
        self.total_spent_label.text = "Total Spent: $0.00"
        self.total_income_label.text = "Total Income: $0.00"
        # Reinitialize ML engine without a user (or later with a new username)
        self.ml_engine = SpentML(username=None)

    def __init__(self, username=None, **kwargs):
        super(InsightsScreen, self).__init__(**kwargs)
        # Initialize the ML engine with the given username so that spending/income is user-specific.
        self.ml_engine = SpentML(username=username)
        self.date_str = ""  # Holds the selected date

        # Root layout for MenuBar and content
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10),
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.title_label = MDLabel(
            text="Transaction Categorization & Insights (ML Version)",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(48)
        )
        self.layout.add_widget(self.title_label)

        self.info_label = MDLabel(
            text="Enter a transaction or income. Spending is classified using a Naive Bayes model. You can correct categories if needed.",
            font_style="Body1",
            halign="center",
            size_hint_y=None,
            height=dp(48)
        )
        self.layout.add_widget(self.info_label)

        # --- Transaction Input Row ---
        self.input_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(48)
        )
        self.date_btn = MDRaisedButton(
            text="Pick Date",
            on_release=self.open_date_picker,
            size_hint=(None, None),
            width=dp(80),
            height=dp(48)
        )
        self.desc_input = MDTextField(
            hint_text="Transaction Description",
            size_hint=(0.4, None),
            height=dp(48)
        )
        self.amt_input = MDTextField(
            hint_text="Amount",
            size_hint=(0.2, None),
            height=dp(48)
        )
        self.add_btn = MDRaisedButton(
            text="Add Transaction",
            on_release=self.add_transaction,
            size_hint=(None, None),
            width=dp(120),
            height=dp(48)
        )
        self.input_row.add_widget(self.date_btn)
        self.input_row.add_widget(self.desc_input)
        self.input_row.add_widget(self.amt_input)
        self.input_row.add_widget(self.add_btn)
        self.layout.add_widget(self.input_row)

        # --- Income Input Row ---
        self.income_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(48)
        )
        self.income_source_input = MDTextField(
            hint_text="Income Source",
            size_hint=(0.4, None),
            height=dp(48)
        )
        self.income_amount_input = MDTextField(
            hint_text="Income Amount",
            size_hint=(0.2, None),
            height=dp(48)
        )
        self.add_income_btn = MDRaisedButton(
            text="Add Income",
            on_release=self.add_income,
            size_hint=(None, None),
            width=dp(120),
            height=dp(48)
        )
        self.income_row.add_widget(self.income_source_input)
        self.income_row.add_widget(self.income_amount_input)
        self.income_row.add_widget(self.add_income_btn)
        self.layout.add_widget(self.income_row)

        # --- Status Label ---
        self.status_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(48)
        )
        self.layout.add_widget(self.status_label)

        # --- Correction Row ---
        self.correction_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(48)
        )
        self.corr_desc_input = MDTextField(
            hint_text="Desc to correct (exact text)",
            size_hint=(0.4, None),
            height=dp(48)
        )
        self.corr_cat_input = MDTextField(
            hint_text="New Category",
            size_hint=(0.3, None),
            height=dp(48)
        )
        self.corr_btn = MDRaisedButton(
            text="Correct",
            on_release=self.correct_category,
            size_hint=(None, None),
            width=dp(80),
            height=dp(48)
        )
        self.correction_row.add_widget(self.corr_desc_input)
        self.correction_row.add_widget(self.corr_cat_input)
        self.correction_row.add_widget(self.corr_btn)
        self.layout.add_widget(self.correction_row)

        self.corr_status_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(48)
        )
        self.layout.add_widget(self.corr_status_label)

        # --- Compare Months Row ---
        self.compare_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(48)
        )
        self.m1_input = MDTextField(
            hint_text="Month1 (YYYY-MM)",
            size_hint=(0.3, None),
            height=dp(48)
        )
        self.m2_input = MDTextField(
            hint_text="Month2 (YYYY-MM)",
            size_hint=(0.3, None),
            height=dp(48)
        )
        self.compare_btn = MDRaisedButton(
            text="Compare",
            on_release=self.compare_months,
            size_hint=(None, None),
            width=dp(80),
            height=dp(48)
        )
        self.compare_row.add_widget(self.m1_input)
        self.compare_row.add_widget(self.m2_input)
        self.compare_row.add_widget(self.compare_btn)
        self.layout.add_widget(self.compare_row)

        self.compare_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(48)
        )
        self.layout.add_widget(self.compare_label)

        # --- Totals Labels ---
        self.total_spent_label = MDLabel(
            text="Total Spent: $0.00",
            halign="center",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(32)
        )
        self.total_income_label = MDLabel(
            text="Total Income: $0.00",
            halign="center",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(32)
        )
        self.layout.add_widget(self.total_spent_label)
        self.layout.add_widget(self.total_income_label)

        # --- Chart Display Area ---
        self.chart_box = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(300)
        )
        self.layout.add_widget(self.chart_box)

        # --- Chart Month Input and Chart Buttons Row ---
        self.chart_month_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(48)
        )
        self.chart_month_input = MDTextField(
            hint_text="Month for chart (YYYY-MM)",
            size_hint=(0.3, None),
            height=dp(48)
        )
        self.bar_btn = MDRaisedButton(
            text="Bar Chart",
            on_release=self.show_bar_chart,
            size_hint=(None, None),
            width=dp(80),
            height=dp(48)
        )
        self.pie_btn = MDRaisedButton(
            text="Pie Chart",
            on_release=self.show_pie_chart,
            size_hint=(None, None),
            width=dp(80),
            height=dp(48)
        )
        self.chart_month_box.add_widget(self.chart_month_input)
        self.chart_month_box.add_widget(self.bar_btn)
        self.chart_month_box.add_widget(self.pie_btn)
        self.layout.add_widget(self.chart_month_box)

        self.forecast_btn = MDRaisedButton(
            text="Go to Forecasting",
            size_hint=(None, None),
            width=dp(180),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_forecasting
        )
        self.layout.add_widget(self.forecast_btn)

        self.scroll_view.add_widget(self.layout)
        self.root_layout.add_widget(self.scroll_view)
        self.add_widget(self.root_layout)

        Clock.schedule_once(self.add_menu_bar, 0)

    def add_menu_bar(self, dt):
        menu = MenuBar(screen_manager=self.manager)
        self.root_layout.add_widget(menu, index=0)

    # -------------------------
    # Date Picker (Using CustomCalendarPopup)
    # -------------------------
    def open_date_picker(self, instance):
        date_dialog = CustomCalendarPopup(callback=self.on_date_chosen)
        date_dialog.open()

    def on_date_chosen(self, date_obj):
        self.date_str = date_obj.strftime("%Y-%m-%d")
        self.date_btn.text = self.date_str

    # -------------------------
    # Add Transaction
    # -------------------------
    def add_transaction(self, instance):
        if not self.date_str:
            self.status_label.text = "Pick a date first."
            return
        desc = self.desc_input.text.strip()
        amt_txt = self.amt_input.text.strip()
        if not desc or not amt_txt:
            self.status_label.text = "Fill description and amount."
            return
        try:
            amt = float(amt_txt)
        except ValueError:
            self.status_label.text = "Amount must be a number."
            return
        ym = self.date_str[:7]
        self.ml_engine.add_transaction(ym, desc, amt)
        self.status_label.text = f"Added: {desc} -> {amt} (predicted cat)."
        self.desc_input.text = ""
        self.amt_input.text = ""

    # -------------------------
    # Add Income
    # -------------------------
    def add_income(self, instance):
        if not self.date_str:
            self.status_label.text = "Pick a date first."
            return
        source = self.income_source_input.text.strip()
        amt_txt = self.income_amount_input.text.strip()
        if not source or not amt_txt:
            self.status_label.text = "Fill income source and amount."
            return
        try:
            amt = float(amt_txt)
        except ValueError:
            self.status_label.text = "Income amount must be a number."
            return
        ym = self.date_str[:7]
        # Record income as negative so it aggregates as income.
        self.ml_engine.add_transaction(ym, "income", -amt)
        self.status_label.text = f"Added Income: {source} -> {amt}"
        self.income_source_input.text = ""
        self.income_amount_input.text = ""

    # -------------------------
    # Correct Category
    # -------------------------
    def correct_category(self, instance):
        d = self.corr_desc_input.text.strip()
        c = self.corr_cat_input.text.strip()
        if not d or not c:
            self.corr_status_label.text = "Enter old desc & new category."
            return
        self.ml_engine.correct_category(d, c)
        self.corr_status_label.text = f"Corrected: '{d}' is now '{c}'"
        self.corr_desc_input.text = ""
        self.corr_cat_input.text = ""

    # -------------------------
    # Compare Months
    # -------------------------
    def compare_months(self, instance):
        m1 = self.m1_input.text.strip()
        m2 = self.m2_input.text.strip()
        if not m1 or not m2:
            self.compare_label.text = "Enter two months (YYYY-MM)."
            return
        msg = self.ml_engine.compare_months(m1, m2)
        self.compare_label.text = msg

    # -------------------------
    # Helper: Filter Spending Data and Include Recurring Items
    # -------------------------
    def _filter_spending_data(self, cat_dict):
        """
        Returns a tuple: (filtered_data, total_spent, total_income)
        - Only positive spending (excluding income) is included in filtered_data.
        - Negative values or the "income" category are summed as total_income.
        - Also, recurring expense subscriptions (from users.json) are added:
              • Monthly: add the amount once.
              • Weekly: add 4 times the amount.
        - Additionally, recurring income entries (if any) are added:
              • For monthly recurring income: add the income (as negative) to total_income.
              • For weekly recurring income: add 4 times the income (as negative) to total_income.
              • Annual recurring income is not auto-added.
        Recurring entries with an amount of 0 are skipped.
        """
        # Filter spending: only positive amounts and ignore the "income" category.
        filtered = {cat: amt for cat, amt in cat_dict.items() if amt > 0 and cat.lower() != "income"}
        total_spent = sum(filtered.values())
        total_income = sum(abs(amt) for cat, amt in cat_dict.items() if amt < 0 or cat.lower() == "income")

        users = load_users()
        if self.ml_engine.username and self.ml_engine.username in users:
            user_record = users[self.ml_engine.username]
            # Process recurring expense subscriptions.
            recurring = user_record.get("recurring", [])
            for sub in recurring:
                freq = sub.get("frequency", "").lower()
                cat = sub.get("category", "Misc")
                amount = sub.get("amount", 0)
                if amount != 0:
                    if freq == "monthly":
                        filtered[cat] = filtered.get(cat, 0) + amount
                        total_spent += amount
                    elif freq == "weekly":
                        weekly_total = 4 * amount
                        filtered[cat] = filtered.get(cat, 0) + weekly_total
                        total_spent += weekly_total
            # Process recurring income.
            recurring_income = user_record.get("recurring_income", [])
            for inc in recurring_income:
                freq = inc.get("frequency", "").lower()
                amount = inc.get("amount", 0)
                if amount != 0:
                    if freq == "monthly":
                        total_income += abs(amount)
                    elif freq == "weekly":
                        total_income += abs(4 * amount)
                    # Annual recurring income is added only when manually input.
        return filtered, total_spent, total_income

    # -------------------------
    # Show Charts (User-Specific)
    # -------------------------
    def show_bar_chart(self, instance):
        self.chart_box.clear_widgets()
        m = self.chart_month_input.text.strip()
        if not m:
            return
        if self.ml_engine.username:
            cat_dict = self.ml_engine.user_spending[self.ml_engine.username].get(m, {})
        else:
            cat_dict = self.ml_engine.monthly_spend.get(m, {})
        filtered_data, total_spent, total_income = self._filter_spending_data(cat_dict)
        self.total_spent_label.text = f"Total Spent: ${total_spent:.2f}"
        self.total_income_label.text = f"Total Income: ${total_income:.2f}"
        bar_texture = create_category_bar(filtered_data)
        bar_image = Image(texture=bar_texture, size_hint=(1, 1))
        self.chart_box.add_widget(bar_image)

    def show_pie_chart(self, instance):
        self.chart_box.clear_widgets()
        m = self.chart_month_input.text.strip()
        if not m:
            return
        if self.ml_engine.username:
            cat_dict = self.ml_engine.user_spending[self.ml_engine.username].get(m, {})
        else:
            cat_dict = self.ml_engine.monthly_spend.get(m, {})
        filtered_data, total_spent, total_income = self._filter_spending_data(cat_dict)
        self.total_spent_label.text = f"Total Spent: ${total_spent:.2f}"
        self.total_income_label.text = f"Total Income: ${total_income:.2f}"
        pie_texture = create_category_pie(filtered_data)
        pie_widget = Image(texture=pie_texture, size_hint=(1, 1))
        self.chart_box.add_widget(pie_widget)

    def go_to_forecasting(self, instance):
        self.manager.current = 'forecast'
