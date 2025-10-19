from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from config import Config
from models import db, User, Syringe, SyringeHistory

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context processor to inject datetime into all templates
@app.context_processor
def inject_datetime():
    return dict(datetime=datetime)

# Create tables and default admin at startup
with app.app_context():
    db.create_all()
    existing_admin = db.session.execute(
        db.select(User).filter_by(username='admin')
    ).scalar_one_or_none()
    if not existing_admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

# ===== Landing / public pages =====
@app.route('/')
def landing():
    return render_template('landing/home.html')

@app.route('/about')
def about():
    return render_template('landing/about.html')

@app.route('/features')
def features():
    return render_template('landing/features.html')

@app.route('/contact')
def contact():
    return render_template('landing/contact.html')

@app.route('/news')
def news():
    return render_template('landing/news.html')

@app.route('/investors')
def investors():
    return render_template('landing/investors.html')

# ===== Privacy Policy =====
@app.route('/privacy')
def privacy():
    return render_template('landing/privacy.html')

# ===== Login / Logout =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

# ===== Dashboard / Syringe pages =====
@app.route('/dashboard')
@login_required
def dashboard():
    syringes = db.session.execute(
        db.select(Syringe).order_by(Syringe.id)
    ).scalars().all()
    return render_template('dashboard.html', syringes=syringes)

@app.route('/syringe/add', methods=['GET', 'POST'])
@login_required
def add_syringe():
    if request.method == 'POST':
        syringe_id = request.form.get('syringe_id', '').strip()

        if not syringe_id:
            flash('Syringe ID is required.', 'warning')
            return redirect(url_for('add_syringe'))

        exists = db.session.execute(
            db.select(Syringe).filter_by(syringe_id=syringe_id)
        ).scalar_one_or_none()
        if exists:
            flash('Syringe ID already exists!', 'warning')
            return redirect(url_for('add_syringe'))

        new_syringe = Syringe(
            syringe_id=syringe_id,
            status='Available',
            patient_info=''
        )
        db.session.add(new_syringe)
        db.session.commit()
        flash('Syringe added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('syringe_add.html')

@app.route('/syringe/<int:id>', methods=['GET', 'POST'])
@login_required
def syringe_detail(id):
    syringe = db.session.get(Syringe, id)
    if not syringe:
        abort(404)

    if request.method == 'POST':
        old_status = syringe.status
        new_status = request.form.get('status', syringe.status)
        syringe.status = new_status
        syringe.patient_info = request.form.get('patient_info', '') or ''
        syringe.last_updated = datetime.utcnow()

        hist = SyringeHistory(
            syringe_id=syringe.id,
            old_status=old_status,
            new_status=new_status,
            updated_by=current_user.username
        )
        db.session.add(hist)
        db.session.commit()

        flash('Syringe updated!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('syringe_detail.html', syringe=syringe)

@app.route('/syringe/<int:id>/history')
@login_required
def syringe_history(id):
    syringe = db.session.get(Syringe, id)
    if not syringe:
        abort(404)

    history = db.session.execute(
        db.select(SyringeHistory)
          .filter_by(syringe_id=id)
          .order_by(SyringeHistory.timestamp.desc())
    ).scalars().all()

    return render_template('history.html', syringe=syringe, history=history)

if __name__ == '__main__':
    app.run(debug=True)
