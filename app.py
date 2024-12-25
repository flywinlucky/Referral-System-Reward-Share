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
    link_name = db.Column(db.String(150), nullable=False)  # New field for link name
    redirect_link = db.Column(db.String(150), nullable=False)
    referral_link = db.Column(db.String(150), unique=True, nullable=False)
    click_count = db.Column(db.Integer, default=0)
    income = db.Column(db.Float, default=0.0)


class GlobalStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_clicks = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)


def generate_unique_code():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(6))


@app.route('/')
def dashboard():
    referrals = Referral.query.all()

    # Ensure global stats exist
    stats = GlobalStats.query.first()
    if not stats:
        stats = GlobalStats(total_clicks=0, total_revenue=0.0)
        db.session.add(stats)
        db.session.commit()

    return render_template('dashboard.html', referrals=referrals, stats=stats)


@app.route('/generate', methods=['POST'])
def generate_referral():
    link_name = request.form.get('link_name')  # Get link name from form
    redirect_link = request.form.get('redirect_link')
    if redirect_link and link_name:
        unique_code = generate_unique_code()
        referral_link = f'https://flask-test-53ar.onrender.com/ref?code={unique_code}'  # Change to your deployment URL https://flask-test-53ar.onrender.com  http://127.0.0.1:5000/
        new_referral = Referral(link_name=link_name, redirect_link=redirect_link, referral_link=referral_link)
        db.session.add(new_referral)
        db.session.commit()
    return redirect('/')


@app.route('/ref', methods=['GET'])
def handle_referral():
    code = request.args.get('code')
    referral = Referral.query.filter(Referral.referral_link.contains(f'code={code}')).first()
    if referral:
        # Increment click count for referral
        referral.click_count += 1

        # Update global stats
        stats = GlobalStats.query.first()
        stats.total_clicks += 1
        db.session.commit()

        # Redirect to the original link with the referral code
        original_url = referral.redirect_link
        referral_url_with_code = f"{original_url}?code={code}"
        return redirect(referral_url_with_code)

    return "Referral link not found.", 404


@app.route('/purchase<refer_name>income<income_amount>', methods=['GET'])
def purchase(refer_name, income_amount):
    try:
        income_amount = float(income_amount)
    except ValueError:
        return "Invalid income amount.", 400

    referral = Referral.query.filter(Referral.referral_link.contains(refer_name)).first()
    if referral:
        referral.income += income_amount

        # Update global revenue
        stats = GlobalStats.query.first()
        stats.total_revenue += income_amount
        db.session.commit()
        return redirect('/')
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
    app.run(debug=True)
