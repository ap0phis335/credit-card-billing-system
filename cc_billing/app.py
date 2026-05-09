from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "creditcardproject"


# =========================================
# TEMPORARY STORAGE
# =========================================
# Later replace with SQLite / MySQL

users = {}


# =========================================
# HOME PAGE
# =========================================
@app.route('/')
def home():
    return render_template('index.html')


# =========================================
# SIGNUP
# =========================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # Prevent duplicate signup
        if email in users:
            return "User already exists"

        # Create user
        users[email] = {
            "password": password,

            # Card data
            "card": None,

            # Transactions list
            "transactions": []
        }

        # Login user after signup
        session['user'] = email

        # Go to add card page
        return redirect(url_for('add_card'))

    return render_template('signup.html')


# =========================================
# LOGIN
# =========================================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        if email in users:

            # Check password
            if users[email]['password'] == password:

                session['user'] = email

                # If card not added yet
                if users[email]['card'] is None:
                    return redirect(url_for('add_card'))

                # Otherwise dashboard
                return redirect(url_for('dashboard'))

        return "Invalid email or password"

    return render_template('login.html')


# =========================================
# ADD CARD
# =========================================
@app.route('/add-card', methods=['GET', 'POST'])
def add_card():

    # User must login first
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        card_name = request.form['card_name']
        last4 = request.form['last4']
        limit = int(request.form['limit'])
        billing_date = request.form['billing_date']
        due_date = request.form['due_date']

        # Store card inside current user
        users[session['user']]['card'] = {
            "card_name": card_name,
            "last4": last4,
            "limit": limit,
            "billing_date": billing_date,
            "due_date": due_date
        }

        return redirect(url_for('dashboard'))

    return render_template('add_card.html')


# =========================================
# DASHBOARD
# =========================================
@app.route('/dashboard')
def dashboard():

    # Protect route
    if 'user' not in session:
        return redirect(url_for('login'))

    current_user = users[session['user']]

    card = current_user['card']
    transactions = current_user['transactions']

    # =====================================
    # CALCULATIONS
    # =====================================

    total_spent = sum(
        t['amount']
        for t in transactions
        if t['type'] == 'debit'
    )

    total_paid = sum(
        t['amount']
        for t in transactions
        if t['type'] == 'credit'
    )

    balance = total_spent - total_paid

    available_credit = card['limit'] - balance

    minimum_due = max(balance * 0.05, 100)

    # =====================================
    # SEND DATA TO HTML
    # =====================================

    return render_template(
        'dashboard.html',

        # Card
        card=card,

        # Transactions
        transactions=transactions,

        # Calculations
        total_spent=total_spent,
        total_paid=total_paid,
        balance=balance,
        available_credit=available_credit,
        minimum_due=minimum_due
    )


# =========================================
# ADD TRANSACTION
# =========================================
@app.route('/add-transaction', methods=['POST'])
def add_transaction():

    if 'user' not in session:
        return redirect(url_for('login'))

    description = request.form['description']
    amount = int(request.form['amount'])
    transaction_type = request.form['type']

    # Add transaction
    users[session['user']]['transactions'].append({
        "desc": description,
        "amount": amount,
        "type": transaction_type
    })

    return redirect(url_for('dashboard'))


# =========================================
# LOGOUT
# =========================================
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('home'))


# =========================================
# RUN APP
# =========================================
if __name__ == '__main__':
    app.run(debug=True)