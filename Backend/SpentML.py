import json
import os
from collections import defaultdict

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

ML_DATA_FILE = "spent_ml_data.json"


def load_users():
    USERS_FILE = "users.json"
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


class SpentML:
    """
    A minimal scikit-learn approach to text categorization of spending.

    Global training data (training_samples) is used for categorization,
    while spending data is stored globally (monthly_spend) and per user (user_spending).
    Every transaction is recorded individually in self.transactions for future corrections.

    Additionally, when a username is provided, the class applies onboarding adjustments
    (recurring income and recurring expenses) from the users.json file. For recurring income:
      - If pay_type is "monthly", the monthly_income (e.g., "15k") is converted and added (as a negative value).
      - If pay_type is "annually", the monthly income is computed as annual_income/4.
    For recurring bills, each bill in the onboarding "bills" array is applied:
      - "monthly" bills are added once,
      - "weekly" bills are multiplied by 4.
    Adjustments are only applied once per month.
    """

    def __init__(self, username=None):
        self.username = username

        self.training_samples = []  # list of [desc, category]
        # Global aggregated spending by month.
        self.monthly_spend = defaultdict(lambda: defaultdict(float))
        # User-specific spending: {username: { "YYYY-MM": { "Category": amount, ... } } }
        self.user_spending = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        # Individual transactions.
        self.transactions = []

        self.vectorizer = CountVectorizer()
        self.classifier = MultinomialNB()
        self.is_fitted = False

        self.load_data()
        if self.training_samples:
            self.train_full()

    def load_data(self):
        if not os.path.exists(ML_DATA_FILE):
            return
        with open(ML_DATA_FILE, "r") as f:
            data = json.load(f)
        self.training_samples = data.get("training_samples", [])
        loaded_global = data.get("monthly_spend", {})
        for ym, cat_dict in loaded_global.items():
            self.monthly_spend[ym] = defaultdict(float, cat_dict)
        loaded_users = data.get("user_spending", {})
        for user, month_dict in loaded_users.items():
            for ym, cat_dict in month_dict.items():
                self.user_spending[user][ym] = defaultdict(float, cat_dict)
        self.transactions = data.get("transactions", [])

    def save_data(self):
        data = {
            "training_samples": self.training_samples,
            "monthly_spend": {ym: dict(cat_dict) for ym, cat_dict in self.monthly_spend.items()},
            "user_spending": {
                user: {ym: dict(cat_dict) for ym, cat_dict in month_dict.items()}
                for user, month_dict in self.user_spending.items()
            },
            "transactions": self.transactions
        }
        with open(ML_DATA_FILE, "w") as f:
            json.dump(data, f)

    def train_full(self):
        descs = [s[0] for s in self.training_samples]
        cats = [s[1] for s in self.training_samples]
        if descs:
            X = self.vectorizer.fit_transform(descs)
            self.classifier.fit(X, cats)
            self.is_fitted = True

    def partial_fit_sample(self, desc, cat):
        self.training_samples.append([desc, cat])
        self.train_full()
        self.save_data()

    def predict_category(self, desc):
        if not self.is_fitted:
            return "Misc"
        X = self.vectorizer.transform([desc])
        pred = self.classifier.predict(X)
        return pred[0]

    def _convert_income(self, income_str):
        """Convert strings like '15k' to float 15000."""
        income_str = income_str.lower().strip()
        if income_str.endswith("k"):
            return float(income_str[:-1]) * 1000
        return float(income_str)

    def apply_onboarding_adjustments(self, date_ym: str):
        """
        Apply recurring income and recurring expense adjustments from the user's onboarding info
        for the given month (date_ym). Adjustments are applied only once per month.
        """
        if not self.username:
            return
        users = load_users()
        if self.username not in users:
            return
        user_record = users[self.username]
        onboarding = user_record.get("onboarding", {})
        # Check if adjustments for this month have already been applied.
        if self.user_spending[self.username].get(date_ym, {}).get("__adjusted__", False):
            return

        # Process recurring income.
        pay_type = onboarding.get("pay_type", "monthly").lower()
        monthly_income_str = onboarding.get("monthly_income", "0")
        income_value = self._convert_income(monthly_income_str)
        if pay_type == "monthly":
            self.user_spending[self.username][date_ym]["income"] -= income_value
        elif pay_type == "annually":
            self.user_spending[self.username][date_ym]["income"] -= income_value / 4

        # Process recurring bills (expenses).
        bills = onboarding.get("bills", [])
        for bill in bills:
            freq = bill.get("frequency", "").lower()
            try:
                bill_amount = float(bill.get("amount", 0))
            except ValueError:
                bill_amount = 0
            bill_cat = bill.get("description", "Misc")
            if bill_amount != 0:
                if freq == "monthly":
                    self.user_spending[self.username][date_ym][bill_cat] += bill_amount
                elif freq == "weekly":
                    self.user_spending[self.username][date_ym][bill_cat] += 4 * bill_amount

        # Mark this month as adjusted.
        self.user_spending[self.username][date_ym]["__adjusted__"] = True
        self.save_data()

    def add_transaction(self, date_ym: str, desc: str, amount: float):
        cat = self.predict_category(desc)
        self.monthly_spend[date_ym][cat] += amount
        if self.username:
            # Ensure recurring income/expense adjustments for this month are applied.
            self.apply_onboarding_adjustments(date_ym)
            self.user_spending[self.username][date_ym][cat] += amount
        self.transactions.append({
            "date_ym": date_ym,
            "desc": desc,
            "amount": amount,
            "category": cat
        })
        self.save_data()

    def correct_category(self, desc: str, new_cat: str):
        for t in self.transactions:
            if t["desc"] == desc and t["category"] != new_cat:
                old_cat = t["category"]
                amount = t["amount"]
                date_ym = t["date_ym"]
                self.monthly_spend[date_ym][old_cat] -= amount
                self.monthly_spend[date_ym][new_cat] += amount
                if self.username:
                    self.user_spending[self.username][date_ym][old_cat] -= amount
                    self.user_spending[self.username][date_ym][new_cat] += amount
                t["category"] = new_cat
        self.partial_fit_sample(desc, new_cat)
        self.save_data()

    def compare_months(self, m1: str, m2: str):
        if self.username:
            s1 = self.user_spending[self.username].get(m1, {})
            s2 = self.user_spending[self.username].get(m2, {})
        else:
            s1 = self.monthly_spend.get(m1, {})
            s2 = self.monthly_spend.get(m2, {})
        cats = set(s1.keys()) | set(s2.keys())
        diffs = []
        for c in cats:
            old_v = s1.get(c, 0.0)
            new_v = s2.get(c, 0.0)
            change = new_v - old_v
            diffs.append((c, old_v, new_v, change))
        diffs.sort(key=lambda x: abs(x[3]), reverse=True)
        if diffs:
            c, ov, nv, ch = diffs[0]
            if ch >= 0:
                msg = f"You spent {ch:.2f} more on {c} in {m2} vs {m1}."
            else:
                msg = f"You spent {-ch:.2f} less on {c} in {m2} vs {m1}."
        else:
            msg = "No categories to compare."
        return {
            'differences': diffs,
            'top_change_summary': msg
        }
