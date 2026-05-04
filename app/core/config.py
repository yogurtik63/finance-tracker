import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

EXPENSE_CATEGORIES = {"food", "gift", "bills"}
INCOME_CATEGORIES = {"gift", "pay", "investments"}