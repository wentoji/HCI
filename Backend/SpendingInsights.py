import datetime
from collections import defaultdict


class SpendingInsights:
    """
    A backend class that:
    1. Categorizes transactions based on simple keyword logic (placeholder for real ML).
    2. Tracks monthly spending by category.
    3. Generates insights (biggest monthly change, etc.).
    """

    def __init__(self):
        # Keywords -> Category mapping (expand or refine as you like)
        # "shoes" -> "Clothing"
        # "grocery", "supermarket" -> "Groceries"
        self.keyword_map = {
            'shoes': 'Clothing',
            'shirt': 'Clothing',
            'pants': 'Clothing',
            'grocery': 'Groceries',
            'supermarket': 'Groceries',
            'restaurant': 'Dining',
            'cafe': 'Dining',
            'electricity': 'Utilities',
            'water': 'Utilities',
            'rent': 'Housing',
            'mortgage': 'Housing',
            # Add more keywords as needed
        }

        # Data structure to track spending:
        # e.g. self.monthly_spend['2023-03']['Groceries'] = 120.50
        self.monthly_spend = defaultdict(lambda: defaultdict(float))

    def categorize_transaction(self, description: str) -> str:
        """
        A naive approach that looks for known keywords.
        If found, returns the matched category;
        otherwise, returns 'Misc' or something.
        """

        desc_lower = description.lower()
        for kw, cat in self.keyword_map.items():
            if kw in desc_lower:
                return cat
        return "Misc"

    def add_transaction(self, date_str: str, description: str, amount: float):
        """
        1) Parse the date (YYYY-MM-DD or similar).
        2) Extract year-month as the key (YYYY-MM).
        3) Categorize the transaction.
        4) Add to the aggregator for that month & category.
        """

        # Convert "2023-05-18" to "2023-05"
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        year_month = date_obj.strftime("%Y-%m")

        category = self.categorize_transaction(description)
        self.monthly_spend[year_month][category] += amount

    def compare_months(self, month1: str, month2: str):
        """
        Compare the category spending for two months, highlight biggest difference.

        Returns:
          A dict with { 'increases': [...], 'decreases': [...], 'summary': 'some summary' }
          or just a string summary, your call.
        """
        cat_spend1 = self.monthly_spend[month1]
        cat_spend2 = self.monthly_spend[month2]

        # Gather all categories from both months
        all_cats = set(cat_spend1.keys()) | set(cat_spend2.keys())

        diffs = []
        for cat in all_cats:
            val1 = cat_spend1.get(cat, 0.0)
            val2 = cat_spend2.get(cat, 0.0)
            change = val2 - val1  # positive => spent more in month2
            diffs.append((cat, val1, val2, change))

        # Sort by absolute difference descending
        diffs.sort(key=lambda x: abs(x[3]), reverse=True)

        # The category with the biggest absolute difference is diffs[0]
        # Summarize the top difference
        if diffs:
            biggest_cat, old_val, new_val, ch = diffs[0]
            if ch > 0:
                top_diff_msg = f"You spent {ch:.2f} more on {biggest_cat} in {month2} compared to {month1}."
            else:
                top_diff_msg = f"You spent {-ch:.2f} less on {biggest_cat} in {month2} compared to {month1}."
        else:
            top_diff_msg = "No categories found to compare."

        return {
            'differences': diffs,
            'top_change_summary': top_diff_msg
        }

    def monthly_report(self, year_month: str):
        """
        Return a dictionary of categories -> amounts for a specific month.
        e.g. { 'Groceries': 150.0, 'Clothing': 20.0, 'Misc': 10.0 }
        """
        cat_data = self.monthly_spend[year_month]
        return dict(cat_data)

    # Optional: If user corrects the category, we can update the "keyword_map"
    # or store it for an ML approach in the future.
    def user_correct_category(self, old_desc: str, new_cat: str):
        """
        Suppose the user says "shoes" should actually be "Sports" not "Clothing".
        We can update our map. In a real ML approach, we might store a training sample.
        """
        # For naive approach, just add a new keyword for that old_desc:
        key = old_desc.lower().split()[0]  # or some more advanced logic
        self.keyword_map[key] = new_cat
        # Next time, it will pick up the new category.
