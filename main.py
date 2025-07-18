import json
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import uuid

# Функция для загрузки транзакций из JSON
def load_transactions():
    try:
        with open('investments.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Функция для сохранения транзакций в JSON
def save_transactions(transactions):
    with open('investments.json', 'w', encoding='utf-8') as file:
        json.dump(transactions, file, ensure_ascii=False, indent=2)

# Форматирование даты
def format_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').strftime('%d %b %Y')
    except ValueError:
        return date_string

# Форматирование валюты
def format_currency(amount):
    return f"{amount:,.2f}".replace(',', ' ')

# Функция для обновления статистики
def update_stats():
    transactions = load_transactions()
    # Общая стоимость
    total = sum(t['total_cost'] if t['action'] == 'Покупка' else -t['total_cost'] for t in transactions)
    total_value_label.config(text=f"{format_currency(total)} KZT")
    # Количество активов
    assets = set(t['asset'] for t in transactions)
    assets_count_label.config(text=len(assets))
    # Количество транзакций
    transactions_count_label.config(text=len(transactions))

# Функция для построения круговой диаграммы
def plot_pie_chart():
    transactions = load_transactions()
    # Группировка по активам
    asset_totals = {}
    for t in transactions:
        asset = t['asset']
        total_cost = t['total_cost'] if t['action'] == 'Покупка' else -t['total_cost']
        asset_totals[asset] = asset_totals.get(asset, 0) + total_cost

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

# Функция для обновления фильтров
def update_filters():
    transactions = load_transactions()
    # Активы
    assets = ['Все активы'] + sorted(set(t['asset'] for t in transactions))
    filter_asset['values'] = assets
    # Брокеры
    brokers = ['Все брокеры'] + sorted(set(t['broker'] for t in transactions))
    filter_broker['values'] = brokers

# Функция для фильтрации и отображения транзакций
def filter_transactions():
    transactions = load_transactions()
    asset_filter = filter_asset.get()
    action_filter = filter_action.get()
    broker_filter = filter_broker.get()

    filtered = transactions
    if asset_filter != 'Все активы':
        filtered = [t for t in filtered if t['asset'] == asset_filter]
    if action_filter != 'Все действия':
        filtered = [t for t in filtered if t['action'] == action_filter]
    if broker_filter != 'Все брокеры':
        filtered = [t for t in filtered if t['broker'] == broker_filter]

    tree.delete(*tree.get_children())
    empty_state.pack_forget()

    if not filtered:
        empty_state.pack(fill=tk.BOTH, expand=True)
        return

    for t in filtered:
        action_color = '#D1FAE5' if t['action'] == 'Покупка' else '#FEE2E2'
        tree.insert('', 'end', values=(
            format_date(t['date']),
            t['asset'],
            t['action'],
            t['quantity'],
            f"{format_currency(t['price_per_share'])} {t['currency']}",
            f"{format_currency(t['total_cost'])} {t['currency']}",
            t['broker'],
            t['id']
        ), tags=(t['action'],))
        tree.tag_configure('Покупка', background='#D1FAE5')
        tree.tag_configure('Продажа', background='#FEE2E2')

# Функция для открытия модального окна добавления
def open_add_modal():
    def submit():
        try:
            quantity = int(quantity_entry.get())
            price = float(price_per_share_entry.get())
            transaction = {
                'id': str(uuid.uuid4()),
                'date': date_entry.get(),
                'company_name': company_entry.get(),
                'asset': asset_entry.get(),
                'action': action_entry.get(),
                'quantity': quantity,
                'price_per_share': price,
                'total_cost': quantity * price,
                'currency': currency_entry.get(),
                'exchange': exchange_entry.get(),
                'broker': broker_entry.get(),
                'settlement_date': settlement_entry.get(),
                'deal_number': deal_entry.get()
            }
            transactions = load_transactions()
            transactions.append(transaction)
            save_transactions(transactions)
            filter_transactions()
            update_stats()
            update_filters()
            plot_pie_chart()
            modal.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных числовых данных")

    modal = tk.Toplevel(root)
    modal.title("Добавить транзакцию")
    modal.transient(root)
    modal.grab_set()

    # Форма
    tk.Label(modal, text="Дата", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
    date_entry = tk.Entry(modal)
    date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    date_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(modal, text="Название компании", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
    company_entry = tk.Entry(modal)
    company_entry.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(modal, text="Тикер актива", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=2)
    asset_entry = tk.Entry(modal)
    asset_entry.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(modal, text="Действие", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=2)
    action_entry = ttk.Combobox(modal, values=['Покупка', 'Продажа'])
    action_entry.set('Покупка')
    action_entry.grid(row=3, column=1, padx=5, pady=2)

    tk.Label(modal, text="Количество", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=2)
    quantity_entry = tk.Entry(modal)
    quantity_entry.grid(row=4, column=1, padx=5, pady=2)

    tk.Label(modal, text="Цена за акцию", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=2)
    price_per_share_entry = tk.Entry(modal)
    price_per_share_entry.grid(row=5, column=1, padx=5, pady=2)

    tk.Label(modal, text="Валюта", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", padx=5, pady=2)
    currency_entry = ttk.Combobox(modal, values=['KZT', 'USD', 'EUR', 'RUB'])
    currency_entry.set('KZT')
    currency_entry.grid(row=6, column=1, padx=5, pady=2)

    tk.Label(modal, text="Брокер", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky="w", padx=5, pady=2)
    broker_entry = tk.Entry(modal)
    broker_entry.grid(row=7, column=1, padx=5, pady=2)

    tk.Label(modal, text="Биржа", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky="w", padx=5, pady=2)
    exchange_entry = tk.Entry(modal)
    exchange_entry.grid(row=8, column=1, padx=5, pady=2)

    tk.Label(modal, text="Дата расчета", font=("Arial", 10, "bold")).grid(row=9, column=0, sticky="w", padx=5, pady=2)
    settlement_entry = tk.Entry(modal)
    settlement_entry.grid(row=9, column=1, padx=5, pady=2)

    tk.Label(modal, text="Номер сделки", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky="w", padx=5, pady=2)
    deal_entry = tk.Entry(modal)
    deal_entry.grid(row=10, column=1, padx=5, pady=2)

    tk.Button(modal, text="Отмена", command=modal.destroy).grid(row=11, column=0, padx=5, pady=10)
    tk.Button(modal, text="Сохранить", command=submit, bg="#2563EB", fg="white").grid(row=11, column=1, padx=5, pady=10)

# Функция для открытия модального окна редактирования
def open_edit_modal(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    transaction_id = item['values'][7]
    transactions = load_transactions()
    transaction = next((t for t in transactions if t['id'] == transaction_id), None)
    if not transaction:
        return

    def submit():
        try:
            quantity = int(quantity_entry.get())
            price = float(price_per_share_entry.get())
            updated_transaction = {
                'id': transaction_id,
                'date': date_entry.get(),
                'company_name': company_entry.get(),
                'asset': asset_entry.get(),
                'action': action_entry.get(),
                'quantity': quantity,
                'price_per_share': price,
                'total_cost': quantity * price,
                'currency': currency_entry.get(),
                'exchange': exchange_entry.get(),
                'broker': broker_entry.get(),
                'settlement_date': settlement_entry.get(),
                'deal_number': deal_entry.get()
            }
            transactions = load_transactions()
            index = next(i for i, t in enumerate(transactions) if t['id'] == transaction_id)
            transactions[index] = updated_transaction
            save_transactions(transactions)
            filter_transactions()
            update_stats()
            update_filters()
            plot_pie_chart()
            modal.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных числовых данных")

    def delete():
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту транзакцию?"):
            transactions = load_transactions()
            transactions = [t for t in transactions if t['id'] != transaction_id]
            save_transactions(transactions)
            filter_transactions()
            update_stats()
            update_filters()
            plot_pie_chart()
            modal.destroy()

    modal = tk.Toplevel(root)
    modal.title("Редактировать транзакцию")
    modal.transient(root)
    modal.grab_set()

    tk.Label(modal, text="Дата", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
    date_entry = tk.Entry(modal)
    date_entry.insert(0, transaction['date'])
    date_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(modal, text="Название компании", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
    company_entry = tk.Entry(modal)
    company_entry.insert(0, transaction['company_name'])
    company_entry.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(modal, text="Тикер актива", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=2)
    asset_entry = tk.Entry(modal)
    asset_entry.insert(0, transaction['asset'])
    asset_entry.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(modal, text="Действие", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=2)
    action_entry = ttk.Combobox(modal, values=['Покупка', 'Продажа'])
    action_entry.set(transaction['action'])
    action_entry.grid(row=3, column=1, padx=5, pady=2)

    tk.Label(modal, text="Количество", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=2)
    quantity_entry = tk.Entry(modal)
    quantity_entry.insert(0, transaction['quantity'])
    quantity_entry.grid(row=4, column=1, padx=5, pady=2)

    tk.Label(modal, text="Цена за акцию", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", padx=5, pady=2)
    price_per_share_entry = tk.Entry(modal)
    price_per_share_entry.insert(0, transaction['price_per_share'])
    price_per_share_entry.grid(row=5, column=1, padx=5, pady=2)

    tk.Label(modal, text="Валюта", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", padx=5, pady=2)
    currency_entry = ttk.Combobox(modal, values=['KZT', 'USD', 'EUR', 'RUB'])
    currency_entry.set(transaction['currency'])
    currency_entry.grid(row=6, column=1, padx=5, pady=2)

    tk.Label(modal, text="Брокер", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky="w", padx=5, pady=2)
    broker_entry = tk.Entry(modal)
    broker_entry.insert(0, transaction['broker'])
    broker_entry.grid(row=7, column=1, padx=5, pady=2)

    tk.Label(modal, text="Биржа", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky="w", padx=5, pady=2)
    exchange_entry = tk.Entry(modal)
    exchange_entry.insert(0, transaction['exchange'])
    exchange_entry.grid(row=8, column=1, padx=5, pady=2)

    tk.Label(modal, text="Дата расчета", font=("Arial", 10, "bold")).grid(row=9, column=0, sticky="w", padx=5, pady=2)
    settlement_entry = tk.Entry(modal)
    settlement_entry.insert(0, transaction['settlement_date'])
    settlement_entry.grid(row=9, column=1, padx=5, pady=2)

    tk.Label(modal, text="Номер сделки", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky="w", padx=5, pady=2)
    deal_entry = tk.Entry(modal)
    deal_entry.insert(0, transaction['deal_number'])
    deal_entry.grid(row=10, column=1, padx=5, pady=2)

    tk.Button(modal, text="Удалить", command=delete, bg="#DC2626", fg="white").grid(row=11, column=0, padx=5, pady=10, sticky="w")
    tk.Button(modal, text="Отмена", command=modal.destroy).grid(row=11, column=1, padx=5, pady=10, sticky="e")
    tk.Button(modal, text="Сохранить", command=submit, bg="#2563EB", fg="white").grid(row=11, column=1, padx=5, pady=10, sticky="w")

# Основное окно
root = tk.Tk()
root.title("Инвестиционный трекер")
root.configure(bg="#F3F4F6")
root.state('zoomed')

# Заголовок
header_frame = tk.Frame(root, bg="#F3F4F6")
header_frame.pack(pady=20)
tk.Label(header_frame, text="Инвестиционный трекер", font=("Arial", 24, "bold"), bg="#F3F4F6").pack()
tk.Label(header_frame, text="Отслеживайте ваши инвестиции в одном месте", font=("Arial", 12), bg="#F3F4F6", fg="#4B5563").pack()

# Карточки статистики
stats_frame = tk.Frame(root, bg="#F3F4F6")
stats_frame.pack(fill=tk.X, padx=20, pady=10)
total_value_frame = tk.Frame(stats_frame, bg="white", bd=1, relief="solid")
total_value_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
tk.Label(total_value_frame, text="Общая стоимость", bg="white", fg="#6B7280", font=("Arial", 10)).pack(padx=10, pady=5)
total_value_label = tk.Label(total_value_frame, text="0 KZT", bg="white", font=("Arial", 16, "bold"))
total_value_label.pack(padx=10, pady=5)

assets_count_frame = tk.Frame(stats_frame, bg="white", bd=1, relief="solid")
assets_count_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
tk.Label(assets_count_frame, text="Активов", bg="white", fg="#6B7280", font=("Arial", 10)).pack(padx=10, pady=5)
assets_count_label = tk.Label(assets_count_frame, text="0", bg="white", font=("Arial", 16, "bold"))
assets_count_label.pack(padx=10, pady=5)

transactions_count_frame = tk.Frame(stats_frame, bg="white", bd=1, relief="solid")
transactions_count_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
tk.Label(transactions_count_frame, text="Транзакций", bg="white", fg="#6B7280", font=("Arial", 10)).pack(padx=10, pady=5)
transactions_count_label = tk.Label(transactions_count_frame, text="0", bg="white", font=("Arial", 16, "bold"))
transactions_count_label.pack(padx=10, pady=5)

# Основной контент (диаграмма и таблица)
main_frame = tk.Frame(root, bg="#F3F4F6")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Диаграмма
chart_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
tk.Label(chart_frame, text="Распределение активов", font=("Arial", 14, "bold"), bg="white").pack(pady=5)

# Таблица транзакций
transactions_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
transactions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

# Заголовок и кнопка добавления
transactions_header = tk.Frame(transactions_frame, bg="white")
transactions_header.pack(fill=tk.X, pady=5)
tk.Label(transactions_header, text="Транзакции", font=("Arial", 14, "bold"), bg="white").pack(side=tk.LEFT, padx=10)
tk.Button(transactions_header, text="Добавить транзакцию", command=open_add_modal, bg="#2563EB", fg="white").pack(side=tk.RIGHT, padx=10)

# Фильтры
filters_frame = tk.Frame(transactions_frame, bg="#F9FAFB")
filters_frame.pack(fill=tk.X, pady=5)
tk.Label(filters_frame, text="Актив", bg="#F9FAFB", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
filter_asset = ttk.Combobox(filters_frame, values=['Все активы'])
filter_asset.set('Все активы')
filter_asset.pack(side=tk.LEFT, padx=5)
filter_asset.bind('<<ComboboxSelected>>', lambda e: filter_transactions())

tk.Label(filters_frame, text="Действие", bg="#F9FAFB", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
filter_action = ttk.Combobox(filters_frame, values=['Все действия', 'Покупка', 'Продажа'])
filter_action.set('Все действия')
filter_action.pack(side=tk.LEFT, padx=5)
filter_action.bind('<<ComboboxSelected>>', lambda e: filter_transactions())

tk.Label(filters_frame, text="Брокер", bg="#F9FAFB", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
filter_broker = ttk.Combobox(filters_frame, values=['Все брокеры'])
filter_broker.set('Все брокеры')
filter_broker.pack(side=tk.LEFT, padx=5)
filter_broker.bind('<<ComboboxSelected>>', lambda e: filter_transactions())

# Таблица
tree = ttk.Treeview(transactions_frame, columns=('Дата', 'Актив', 'Действие', 'Кол-во', 'Цена', 'Сумма', 'Брокер', 'ID'), show='headings')
tree.heading('Дата', text='Дата')
tree.heading('Актив', text='Актив')
tree.heading('Действие', text='Действие')
tree.heading('Кол-во', text='Кол-во')
tree.heading('Цена', text='Цена')
tree.heading('Сумма', text='Сумма')
tree.heading('Брокер', text='Брокер')
tree.heading('ID', text='')
tree.column('ID', width=0, stretch=False)
tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
tree.bind('<Double-1>', open_edit_modal)

# Пустое состояние
empty_state = tk.Frame(transactions_frame, bg="white")
tk.Label(empty_state, text="Нет транзакций", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
tk.Label(empty_state, text="Начните добавлять транзакции, чтобы отслеживать ваши инвестиции.", font=("Arial", 10), bg="white", fg="#6B7280").pack()
tk.Button(empty_state, text="Добавить первую транзакцию", command=open_add_modal, bg="#2563EB", fg="white").pack(pady=10)

# Инициализация
update_stats()
update_filters()
plot_pie_chart()
filter_transactions()

root.mainloop()