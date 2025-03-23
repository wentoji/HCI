import re
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp

from utils.session import get_user
from utils.AccountManager import load_users, save_users


class OnboardingScreen(MDScreen):
    def __init__(self, **kwargs):
        super(OnboardingScreen, self).__init__(**kwargs)

        # We'll store the user’s onboarding data here
        self.user_data = {
            'pay_type': None,
            'monthly_income': None,
            'pay_day': None,  # e.g. "18th" or "18/10"
            'num_bills': 0,
            'bills': []       # list of dicts: [{desc, freq, amount}, ...]
        }

        # We'll start with just 2 steps; we insert additional steps dynamically
        self.steps = [
            {
                'question': "Do you get paid monthly or annually?",
                'key': 'pay_type',
                'validate': self.validate_pay_type
            },
            {
                'question': "Enter your income (format: e.g. '150k' or '2.2k'):",
                'key': 'monthly_income',
                'validate': self.validate_income
            }
        ]
        self.current_step = 0

        # --------------------------
        # LAYOUT & UI
        # --------------------------

        # Main container for everything
        self.root_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # We'll store the dynamic question/error/input within 'self.layout'
        self.layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # Question label
        self.question_label = MDLabel(
            font_style="H6",  # a nice medium size
            halign="left",
            text=""
        )
        # Error label (red)
        self.error_label = MDLabel(
            text="",
            halign="left",
            theme_text_color="Error"  # will render in red
        )

        # Answer input
        self.answer_input = MDTextField(
            multiline=False,
            size_hint=(1, None),
            height=dp(48)
        )

        # Nav layout (Back/Next)
        self.nav_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(48)
        )

        self.back_button = MDRaisedButton(text="< Back")
        self.next_button = MDRaisedButton(text="Next >")

        self.back_button.bind(on_press=self.go_back)
        self.next_button.bind(on_press=self.go_next)

        self.nav_layout.add_widget(self.back_button)
        self.nav_layout.add_widget(self.next_button)

        # Assemble the main layout
        self.layout.add_widget(self.question_label)
        self.layout.add_widget(self.error_label)
        self.layout.add_widget(self.answer_input)
        self.layout.add_widget(self.nav_layout)

        self.root_layout.add_widget(self.layout)
        self.add_widget(self.root_layout)

        # Show the first step
        self.show_step(0)


    # ----------------------------------------------------------------
    # Step Display / Navigation
    # ----------------------------------------------------------------

    def show_step(self, step_index):
        """Update UI for the current step and clear the input field."""
        if step_index < 0 or step_index >= len(self.steps):
            return

        step_data = self.steps[step_index]
        self.question_label.text = step_data['question']
        self.error_label.text = ""

        # Start with an empty textfield each time
        self.answer_input.text = ""

        # Disable back button on the first step
        self.back_button.disabled = (step_index == 0)

        # If we're on the last step, show "Finish"
        if step_index == len(self.steps) - 1:
            self.next_button.text = "Finish"
        else:
            self.next_button.text = "Next >"

    def go_next(self, instance):
        """When user clicks Next/Finish, validate & store the current answer, then proceed."""
        step_data = self.steps[self.current_step]
        key = step_data['key']
        raw_answer = self.answer_input.text.strip()

        # Validate
        if step_data.get('validate'):
            error_msg = step_data['validate'](raw_answer)
            if error_msg:
                self.error_label.text = f"Error: {error_msg}"
                return

        # Store the validated answer
        self.user_data[key] = raw_answer

        # If user just answered pay_type, insert pay_day step
        if key == 'pay_type' and not any(s['key'] == 'pay_day' for s in self.steps):
            self.insert_pay_day_step(raw_answer)

        # If user just answered monthly_income, insert how-many-bills step
        if key == 'monthly_income' and 'num_bills' not in [s['key'] for s in self.steps]:
            self.insert_num_bills_step()

        # If user just answered num_bills, build steps for the bills
        if key == 'num_bills':
            nb = int(raw_answer)
            # Remove old bill steps if changed
            self.steps = [s for s in self.steps if not s['key'].startswith('bill_')]
            self.build_bill_steps(nb)

        # Move forward or finish
        if self.current_step == len(self.steps) - 1:
            self.complete_onboarding()
        else:
            self.current_step += 1
            self.show_step(self.current_step)

    def go_back(self, instance):
        """Go back one step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step(self.current_step)

    def complete_onboarding(self):
        """All steps done: gather data, save to users.json, then move to main screen."""
        # Gather bills
        nb = int(self.user_data.get('num_bills', 0))
        bills = []
        for i in range(nb):
            desc = self.user_data.get(f"bill_{i}_desc", "")
            freq = self.user_data.get(f"bill_{i}_freq", "")
            amt  = self.user_data.get(f"bill_{i}_amount", "")
            bills.append({
                'description': desc,
                'frequency': freq,
                'amount': amt
            })
        self.user_data['bills'] = bills

        # Store all in users.json under current username
        username = get_user()  # ensure set_user(username) was called after signup
        self.save_onboarding_data(username)

        print("Onboarding complete! Data collected:", self.user_data)

        # Go to main screen (PC or phone)
        self.manager.current = 'pc'


    # ----------------------------------------------------------------
    # Dynamic Steps
    # ----------------------------------------------------------------

    def insert_pay_day_step(self, pay_type):
        """After user picks monthly or annually, ask for the pay day."""
        if pay_type.lower() == 'monthly':
            pay_day_step = {
                'question': "Which day do you get paid each month? (e.g. '1st', '18th', '22nd')",
                'key': 'pay_day',
                'validate': self.validate_monthly_day
            }
        else:
            pay_day_step = {
                'question': "Which day/month do you get paid? (format 'dd/mm', e.g. '18/10')",
                'key': 'pay_day',
                'validate': self.validate_annual_day
            }
        insert_index = self.current_step + 1
        self.steps.insert(insert_index, pay_day_step)

    def insert_num_bills_step(self):
        """After monthly_income, ask how many bills."""
        step = {
            'question': "How many recurring bills / subscriptions do you have?",
            'key': 'num_bills',
            'validate': self.validate_num_bills
        }
        insert_index = self.current_step + 1
        self.steps.insert(insert_index, step)

    def build_bill_steps(self, n):
        """For each bill, add 3 sub-steps: description, frequency, amount."""
        insert_index = self.current_step + 1
        for i in range(n):
            desc_step = {
                'question': f"Recurring Bill #{i+1} description?",
                'key': f"bill_{i}_desc",
                'validate': self.validate_nonempty
            }
            freq_step = {
                'question': f"Recurring Bill #{i+1} frequency? (monthly, annual, weekly)",
                'key': f"bill_{i}_freq",
                'validate': self.validate_frequency
            }
            amt_step = {
                'question': f"Recurring Bill #{i+1} exact amount? (e.g. '15.20', '2000.10')",
                'key': f"bill_{i}_amount",
                'validate': self.validate_amount
            }

            self.steps.insert(insert_index, amt_step)
            self.steps.insert(insert_index, freq_step)
            self.steps.insert(insert_index, desc_step)
            insert_index += 3

    # ----------------------------------------------------------------
    # Save Onboarding Data to JSON
    # ----------------------------------------------------------------

    def save_onboarding_data(self, username):
        """Merge the wizard data into the user’s record in users.json."""
        users = load_users()

        # If for some reason the user doesn't exist, create them
        if username not in users:
            users[username] = {}

        # If it's just a string, that's the hashed password
        if isinstance(users[username], str):
            hashed_pass = users[username]
            users[username] = {'password': hashed_pass}

        # Now store the onboarding data
        users[username]['onboarding'] = self.user_data

        save_users(users)

    # ----------------------------------------------------------------
    # Validation Methods
    # ----------------------------------------------------------------

    def validate_pay_type(self, answer):
        """Pay type must be 'monthly' or 'annually'."""
        valid = ['monthly', 'annually']
        if answer.lower() not in valid:
            return "Please enter 'monthly' or 'annually'."
        return ""

    def validate_income(self, answer):
        """
        Must match pattern like '150k' or '2.2k'.
        We'll allow digits, optional single decimal, then 'k'.
        Regex: ^[0-9]+(\.[0-9]+)?k$
        """
        pattern = r'^[0-9]+(\.[0-9]+)?k$'
        if not re.match(pattern, answer.lower()):
            return "Income must be e.g. '2.2k' or '150k'."
        return ""

    def validate_monthly_day(self, answer):
        """Monthly pay day: '1st', '2nd', '22nd', etc."""
        pattern = r'^\d+(st|nd|rd|th)$'
        if not re.match(pattern, answer.lower()):
            return "Day must be like '1st', '2nd', '22nd', '3rd', etc."
        return ""

    def validate_annual_day(self, answer):
        """Annual pay day: dd/mm, e.g. '18/10'."""
        pattern = r'^\d{1,2}\/\d{1,2}$'
        if not re.match(pattern, answer):
            return "Date must be in format 'dd/mm' e.g. '18/10'."
        return ""

    def validate_num_bills(self, answer):
        """Number of bills must be a non-negative integer."""
        if not answer.isdigit():
            return "Please enter a valid integer number of bills."
        return ""

    def validate_nonempty(self, answer):
        """Ensure it's not empty."""
        if not answer:
            return "This field cannot be empty."
        return ""

    def validate_frequency(self, answer):
        """Bill frequency: 'monthly', 'annual'(ly), 'weekly'."""
        valid = ['monthly', 'annual', 'annually', 'weekly']
        if answer.lower() not in valid:
            return "Enter 'monthly', 'annual'(ly), or 'weekly'."
        return ""

    def validate_amount(self, answer):
        """
        Must be a decimal number with up to 2 decimals (e.g. '15.20', '2000.10').
        """
        pattern = r'^\d+(\.\d{1,2})?$'
        if not re.match(pattern, answer):
            return "Amount must be a number (e.g. '15.20', '2000.10')."
        return ""
