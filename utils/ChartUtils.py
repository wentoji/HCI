import io
import matplotlib.pyplot as plt
from kivy.core.image import Image as CoreImage


def create_category_bar(categories_dict):
    """
    Creates a bar chart from the categories_dict (e.g. {"Groceries": 100, "Dining": 50, ...})
    and returns a Kivy texture that can be displayed using an Image widget.
    """
    # Increase the figure size for better visibility.
    fig, ax = plt.subplots(figsize=(9, 7), dpi=100)

    labels = list(categories_dict.keys())
    values = list(categories_dict.values())

    ax.bar(labels, values, color='blue')
    ax.set_ylabel("Amount")
    ax.set_title("Spending by Category")
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    core_image = CoreImage(buf, ext='png')
    return core_image.texture


def create_category_pie(categories_dict):
    """
    Creates a pie chart from categories_dict and returns a Kivy texture.
    Displays the category percentages along with a title.
    """
    fig, ax = plt.subplots(figsize=(9, 7), dpi=100)

    labels = list(categories_dict.keys())
    values = list(categories_dict.values())
    total = sum(values)

    if total == 0:
        ax.text(0.5, 0.5, "No data", ha='center', va='center', fontsize=12)
    else:
        ax.pie(values, labels=labels, autopct='%1.1f%%')

    ax.set_title("Spending Distribution\nTotal Spent: ${:.2f}".format(total))

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    core_image = CoreImage(buf, ext='png')
    return core_image.texture
