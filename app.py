from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///referrals.db'
db = SQLAlchemy(app)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    redirect_link = db.Column(db.String(150), nullable=False)
    referral_link = db.Column(db.String(150), unique=True, nullable=False)
    click_count = db.Column(db.Integer, default=0)
    income = db.Column(db.Float, default=0.0)

def generate_unique_code():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(6))

@app.route('/')
def dashboard():
    referrals = Referral.query.all()
    return render_template('dashboard.html', referrals=referrals)

@app.route('/generate', methods=['POST'])
def generate_referral():
    redirect_link = request.form.get('redirect_link')
    if redirect_link:
        unique_code = generate_unique_code()
        referral_link = f'https://flask-test.onrender.com/ref?code={unique_code}'
        new_referral = Referral(redirect_link=redirect_link, referral_link=referral_link)
        db.session.add(new_referral)
        db.session.commit()
    return redirect('/')

@app.route('/ref', methods=['GET'])
def handle_referral():
    code = request.args.get('code')
    referral = Referral.query.filter(Referral.referral_link.contains(f'code={code}')).first()
    if referral:
        # Înregistrează clicul
        referral.click_count += 1
        db.session.commit()

        # Construiește URL-ul original cu codul referral adăugat la sfârșit
        original_url = referral.redirect_link
        referral_url_with_code = f"{original_url}?code={code}"  # Adaugă codul referral

        # Redirecționează utilizatorul către URL-ul original cu codul referral
        return redirect(referral_url_with_code)

    return "Referral link not found.", 404

@app.route('/purchase<refer_name>income<income_amount>', methods=['GET'])
def purchase(refer_name, income_amount):
    # Extrage suma de venit și convertește-o în float
    try:
        income_amount = float(income_amount)
    except ValueError:
        return "Invalid income amount.", 400

    # Găsește linkul referral pe baza codului unic din refer_name
    referral = Referral.query.filter(Referral.referral_link.contains(refer_name)).first()
    if referral:
        referral.income += income_amount  # Crește venitul cu suma specificată
        db.session.commit()
        return redirect('/')  # Redirecționează înapoi la tabloul de bord după achiziție reușită
    return "Referral link not found.", 404

@app.route('/delete/<int:referral_id>', methods=['POST'])
def delete_referral(referral_id):
    referral = Referral.query.get(referral_id)
    if referral:
        db.session.delete(referral)
        db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()   #app.run(host='0.0.0.0', port=5000)   app.run(debug=True) 