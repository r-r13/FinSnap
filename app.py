from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)

def generate_ai_tips(entries, total_income, total_expenses, category_totals):
    import random

    tips = []

    if not entries:
        return ["No financial activity recorded yet. Start by adding an income or expense entry!"]

    # 1. Savings Rate Tip
    if total_income > 0:
        savings_rate = round((total_income - total_expenses) / total_income * 100, 2)
        if savings_rate > 90:
            tips.append(random.choice([
                f"You're saving {savings_rate}% of your income — incredible financial discipline!",
                f"Wow! {savings_rate}% of your income is untouched. Keep it up!",
                f"With a {savings_rate}% savings rate, your future self will thank you."
            ]))
        elif savings_rate > 50:
            tips.append(f"You're saving about {savings_rate}% — a healthy cushion!")
        elif savings_rate < 0:
            tips.append("⚠️ You're spending more than you're earning. Try cutting back a bit.")
        else:
            tips.append("You're saving a small portion of your income — consider building up your savings rate.")

    # 2. Highest Spending Category Tip
    if category_totals:
        top_cat = max(category_totals, key=category_totals.get)
        top_amt = category_totals[top_cat]
        tips.append(random.choice([
            f"You're spending the most in {top_cat} — totaling ${top_amt:.2f}. Maybe set a monthly cap?",
            f"Keep an eye on {top_cat} — your biggest expense category at ${top_amt:.2f}.",
            f"Most of your budget is going to {top_cat}. Is that intentional?"
        ]))

    # 3. Missing Category Check (case-insensitive)
    common_cats = ['food', 'transport', 'entertainment', 'bills', 'shopping']
    logged_cats = set(cat.lower() for cat in category_totals.keys())

    for cat in common_cats:
        if cat not in logged_cats:
            tips.append(f"No spending recorded in {cat}. Either you're super frugal or forgot to log it!")

    # 4. Entry count tip
    if len(entries) > 10:
        tips.append("Nice work! You've entered over 10 transactions — consistent tracking is key.")

    return tips


@app.route('/')
def dashboard():
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    c.execute("SELECT * FROM entries")
    entries = c.fetchall()
    conn.close()

    # Calculate totals
    total_income = sum(entry[2] for entry in entries if entry[1] == 'income')
    total_expenses = sum(entry[2] for entry in entries if entry[1] == 'expense')
    remaining = total_income - total_expenses

    # Data for pie chart: expenses by category
    category_totals = {}
    for entry in entries:
        if entry[1] == 'expense':
            category = entry[3]
            category_totals[category] = category_totals.get(category, 0) + entry[2]
    
    ai_tips = generate_ai_tips(entries, total_income, total_expenses, category_totals)

    return render_template('dashboard.html',
                           entries=entries,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           remaining=remaining,
                           category_totals=category_totals,
                           tips=ai_tips)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        entry_type = request.form['entry_type']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        notes = request.form['notes']

        # Save to SQLite
        conn = sqlite3.connect('budget.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO entries (entry_type, amount, category, date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_type, amount, category, date, notes))
        conn.commit()
        conn.close()

        return redirect('/')
    return render_template('add_entry.html')

@app.route('/tips')
def tips():
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    c.execute("SELECT * FROM entries")
    entries = c.fetchall()
    conn.close()

    # Totals
    total_income = sum(entry[2] for entry in entries if entry[1] == 'income')
    total_expenses = sum(entry[2] for entry in entries if entry[1] == 'expense')

    # Categories
    category_totals = {}
    for entry in entries:
        if entry[1] == 'expense':
            cat = entry[3]
            category_totals[cat] = category_totals.get(cat, 0) + entry[2]

    tips = generate_ai_tips(entries, total_income, total_expenses, category_totals)

    return render_template('tips.html', ai_tips=tips)


@app.route('/clear', methods=['POST'])
def clear_entries():
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    c.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
