import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from data import load_transactions, format_date, format_currency

def get_stats():
    transactions = load_transactions()
    total = sum(t['total_cost'] if t['action'] == 'Покупка' else -t['total_cost'] for t in transactions)
    assets = set(t['asset'] for t in transactions)
    return {
        'total': total,
        'assets_count': len(assets),
        'transactions_count': len(transactions)
    }

def get_asset_totals():
    transactions = load_transactions()
    asset_totals = {}
    for t in transactions:
        asset = t['asset']
        total_cost = t['total_cost'] if t['action'] == 'Покупка' else -t['total_cost']
        asset_totals[asset] = asset_totals.get(asset, 0) + total_cost
    return asset_totals

def filter_transactions(asset_filter, action_filter, broker_filter):
    transactions = load_transactions()
    filtered = transactions
    if asset_filter != 'Все активы':
        filtered = [t for t in filtered if t['asset'] == asset_filter]
    if action_filter != 'Все действия':
        filtered = [t for t in filtered if t['action'] == action_filter]
    if broker_filter != 'Все брокеры':
        filtered = [t for t in filtered if t['broker'] == broker_filter]
    return filtered

def plot_pie_chart(chart_frame):
    asset_totals = get_asset_totals()
    labels = []
    sizes = []
    total_sum = sum(asset_totals.values())
    for asset, total in asset_totals.items():
        percentage = (total / total_sum * 100) if total_sum > 0 else 0
        labels.append(f"{asset} ({percentage:.1f}%)")
        sizes.append(total)
    chart_frame_inner = tk.Frame(chart_frame)
    chart_frame_inner.pack(fill=tk.BOTH, expand=True)
    for widget in chart_frame_inner.winfo_children():
        widget.destroy()
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    canvas = FigureCanvasTkAgg(fig, master=chart_frame_inner)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True) 