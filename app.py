"""
Glavna Flask aplikacija za bančni sistem
"""
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timedelta
import secrets

# Uvoz modela in storitev
from model import conn, Kazalec, Stranka, Racun, Paket, Transakcija
from services import BankService

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Inicializacija bančnih storitev
bank = BankService()


# Dekorater za zaščito strani (zahteva prijavo)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Prosimo, prijavite se.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Dekorater za admin dostop
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Nimate dovoljenja za dostop.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Domača stran - preusmeri na dashboard ali login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Prijava uporabnika"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        user_id = data.get('user_id')
        
        # Preveri če je admin
        if user_id == 'admin':
            session['user_id'] = 'admin'
            session['is_admin'] = True
            session['name'] = 'Administrator'
            return jsonify({'success': True, 'redirect': url_for('admin_dashboard')})
        
        # Poskusi najti stranko
        stranka = bank.get_stranka(user_id)
        if stranka:
            session['user_id'] = stranka.id_stranke
            session['is_admin'] = False
            session['name'] = f"{stranka.ime} {stranka.priimek}"
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Napačna ID stranke'}), 401
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Odjava uporabnika"""
    session.clear()
    flash('Uspešno ste se odjavili.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Glavna nadzorna plošča uporabnika"""
    user_id = session['user_id']
    
    # Pridobi podatke o stranki
    stranka = bank.get_stranka(user_id)
    if not stranka:
        flash('Stranka ni najdena.', 'danger')
        return redirect(url_for('logout'))
    
    # Pridobi vse račune stranke
    racuni = bank.get_racuni_stranke(user_id)
    
    # Izračunaj skupno stanje
    total_balance = sum(r['stanje'] for r in racuni)
    
    # Pridobi zadnje transakcije
    recent_transactions = bank.get_recent_transactions(user_id, limit=10)
    
    return render_template('dashboard.html',
                         stranka=stranka,
                         racuni=racuni,
                         total_balance=total_balance,
                         recent_transactions=recent_transactions)


@app.route('/accounts')
@login_required
def accounts():
    """Stran z vsemi računi"""
    user_id = session['user_id']
    racuni = bank.get_racuni_stranke(user_id)
    
    # Za vsak račun pridobi tudi paket
    for racun in racuni:
        racun['paket'] = bank.get_paket_za_racun(racun['IBAN'])
    
    return render_template('accounts.html', racuni=racuni)


@app.route('/account/<iban>')
@login_required
def account_detail(iban):
    """Detajli posameznega računa"""
    user_id = session['user_id']
    
    # Preveri, da račun pripada uporabniku
    racun = bank.get_racun(iban)
    if not racun or racun['id_lastnik'] != user_id:
        flash('Nimate dostopa do tega računa.', 'danger')
        return redirect(url_for('accounts'))
    
    # Pridobi transakcije za ta račun
    transactions = bank.get_transactions_for_account(iban)
    paket = bank.get_paket_za_racun(iban)
    
    return render_template('account_detail.html',
                         racun=racun,
                         transactions=transactions,
                         paket=paket)


@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """Nakazilo med računi"""
    if request.method == 'POST':
        data = request.get_json()
        from_iban = data.get('from_iban')
        to_iban = data.get('to_iban')
        amount = data.get('amount')
        
        try:
            amount_cents = int(float(amount) * 100)
            
            # Preveri, da je pošiljatelj lastnik računa
            racun = bank.get_racun(from_iban)
            if not racun or racun['id_lastnik'] != session['user_id']:
                return jsonify({'success': False, 'message': 'Nimate dostopa do tega računa'}), 403
            
            # Izvedi nakazilo
            success, message = bank.create_transfer(from_iban, to_iban, amount_cents)
            
            if success:
                return jsonify({'success': True, 'message': message})
            else:
                return jsonify({'success': False, 'message': message}), 400
                
        except ValueError:
            return jsonify({'success': False, 'message': 'Napačen znesek'}), 400
    
    # GET zahteva
    user_id = session['user_id']
    racuni = bank.get_racuni_stranke(user_id)
    return render_template('transfer.html', racuni=racuni)


@app.route('/deposit', methods=['POST'])
@login_required
def deposit():
    """Polog denarja na račun"""
    data = request.get_json()
    iban = data.get('iban')
    amount = data.get('amount')
    
    try:
        amount_cents = int(float(amount) * 100)
        
        # Preveri lastništvo
        racun = bank.get_racun(iban)
        if not racun or racun['id_lastnik'] != session['user_id']:
            return jsonify({'success': False, 'message': 'Nimate dostopa'}), 403
        
        success, message = bank.create_deposit(iban, amount_cents)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Napačen znesek'}), 400


@app.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    """Dvig denarja z računa"""
    data = request.get_json()
    iban = data.get('iban')
    amount = data.get('amount')
    
    try:
        amount_cents = int(float(amount) * 100)
        
        # Preveri lastništvo
        racun = bank.get_racun(iban)
        if not racun or racun['id_lastnik'] != session['user_id']:
            return jsonify({'success': False, 'message': 'Nimate dostopa'}), 403
        
        success, message = bank.create_withdrawal(iban, amount_cents)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Napačen znesek'}), 400


@app.route('/packages')
@login_required
def packages():
    """Pregled paketov"""
    available_packages = [
        {
            'tip': 'Basic',
            'cena': 0,
            'osnovni_limit': 50000,  # 500 EUR
            'dnevni_limit': 10000,   # 100 EUR
            'opis': 'Brezplačen osnovni paket'
        },
        {
            'tip': 'Premium',
            'cena': 599,  # 5.99 EUR
            'osnovni_limit': 500000,  # 5000 EUR
            'dnevni_limit': 100000,   # 1000 EUR
            'opis': 'Povečani limiti in dodatne ugodnosti'
        },
        {
            'tip': 'Business',
            'cena': 1999,  # 19.99 EUR
            'osnovni_limit': None,  # Brez limita
            'dnevni_limit': 1000000,  # 10000 EUR
            'opis': 'Za podjetja in visoke zneske'
        }
    ]
    
    user_id = session['user_id']
    racuni = bank.get_racuni_stranke(user_id)
    
    # Dodaj informacije o trenutnih paketih
    for racun in racuni:
        racun['paket'] = bank.get_paket_za_racun(racun['IBAN'])
    
    return render_template('packages.html',
                         available_packages=available_packages,
                         racuni=racuni)


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin nadzorna plošča"""
    stats = bank.get_statistics()
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/customers')
@admin_required
def admin_customers():
    """Seznam vseh strank"""
    stranke = bank.get_all_stranke()
    return render_template('admin/customers.html', stranke=stranke)


@app.route('/admin/transactions')
@admin_required
def admin_transactions():
    """Seznam vseh transakcij"""
    transactions = bank.get_all_transactions(limit=100)
    return render_template('admin/transactions.html', transactions=transactions)


@app.route('/api/account/<iban>/balance')
@login_required
def api_account_balance(iban):
    """API endpoint za stanje računa"""
    racun = bank.get_racun(iban)
    if not racun or racun['id_lastnik'] != session['user_id']:
        return jsonify({'error': 'Nimate dostopa'}), 403
    
    return jsonify({'balance': racun['stanje']})


# Template filters
@app.template_filter('centi_v_eure')
def centi_v_eure(centi):
    """Pretvori cente v eure"""
    if centi is None:
        return '0.00'
    return f"{centi / 100:.2f}"


@app.template_filter('format_iban')
def format_iban(iban):
    """Formatiraj IBAN za prikaz"""
    if not iban:
        return ''
    # Že ima presledke
    return iban


@app.template_filter('format_datum')
def format_datum(datum_str):
    """Formatiraj datum"""
    if not datum_str:
        return ''
    try:
        dt = datetime.fromisoformat(datum_str.replace(' ', 'T'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except:
        return datum_str


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
