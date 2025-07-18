import json
from datetime import datetime

INVESTMENTS_FILE = 'investments.json'

def load_transactions():
    try:
        with open(INVESTMENTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_transactions(transactions):
    with open(INVESTMENTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(transactions, file, ensure_ascii=False, indent=2)

def format_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').strftime('%d %b %Y')
    except ValueError:
        return date_string

def format_currency(amount):
    return f"{amount:,.2f}".replace(',', ' ') 