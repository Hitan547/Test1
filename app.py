from flask import Flask, request, jsonify, session, render_template
from models import db, Admin, PasswordResetToken, Opportunity
from datetime import datetime, timedelta
import bcrypt
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY']                  = os.environ.get('SECRET_KEY', 'qatar-admin-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI']     = os.environ.get('DATABASE_URL', 'sqlite:///qatar_admin.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY']     = True
app.config['SESSION_COOKIE_SAMESITE']     = 'Lax'

db.init_app(app)

with app.app_context():
    db.create_all()


def get_current_admin():
    if 'admin_id' not in session:
        return None
    return Admin.query.get(session['admin_id'])


# ─────────────────────── SERVE UI ───────────────────────

@app.route('/')
def index():
    return render_template('admin.html')


# ─────────────────────── AUTH ───────────────────────

@app.route('/api/signup', methods=['POST'])
def signup():
    data      = request.get_json()
    full_name = (data.get('full_name') or '').strip()
    email     = (data.get('email')     or '').strip().lower()
    password  =  data.get('password')  or ''

    if not all([full_name, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin   = Admin(full_name=full_name, email=email, password_hash=pw_hash)
    db.session.add(admin)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = (data.get('email')    or '').strip().lower()
    password =  data.get('password') or ''
    remember =  data.get('remember_me', False)

    admin = Admin.query.filter_by(email=email).first()

    if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['admin_id'] = admin.id

    if remember:
        session.permanent               = True
        app.permanent_session_lifetime  = timedelta(days=30)
    else:
        session.permanent = False

    return jsonify({'message': 'Login successful', 'email': admin.email, 'name': admin.full_name}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/me', methods=['GET'])
def me():
    admin = get_current_admin()
    if not admin:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'email': admin.email, 'name': admin.full_name}), 200


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data  = request.get_json()
    email = (data.get('email') or '').strip().lower()

    admin = Admin.query.filter_by(email=email).first()
    if admin:
        PasswordResetToken.query.filter_by(admin_id=admin.id, used=False).update({'used': True})
        db.session.commit()

        token      = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        db.session.add(PasswordResetToken(admin_id=admin.id, token=token, expires_at=expires_at))
        db.session.commit()

        reset_url = f"http://localhost:5000/reset-password/{token}"
        print(f"\n{'='*60}")
        print(f"[PASSWORD RESET REQUEST]")
        print(f"Email     : {email}")
        print(f"Reset URL : {reset_url}")
        print(f"Expires   : {expires_at} UTC")
        print(f"{'='*60}\n")

    return jsonify({'message': 'If this email is registered, a reset link has been sent.'}), 200


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token or reset_token.used:
        return render_template('reset_error.html',
                               error='This reset link is invalid or has already been used.')

    if datetime.utcnow() > reset_token.expires_at:
        return render_template('reset_error.html',
                               error='This reset link has expired. Please request a new one from the login page.')

    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm      = request.form.get('confirm_password', '')

        if len(new_password) < 8:
            return render_template('reset_form.html', token=token,
                                   error='Password must be at least 8 characters.')
        if new_password != confirm:
            return render_template('reset_form.html', token=token,
                                   error='Passwords do not match.')

        admin = Admin.query.get(reset_token.admin_id)
        admin.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        reset_token.used    = True
        db.session.commit()
        return render_template('reset_success.html')

    return render_template('reset_form.html', token=token, error=None)


# ─────────────────────── OPPORTUNITIES ───────────────────────

@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    admin = get_current_admin()
    if not admin:
        return jsonify({'error': 'Not authenticated'}), 401

    opps = Opportunity.query.filter_by(admin_id=admin.id)\
                            .order_by(Opportunity.created_at.desc()).all()
    return jsonify([o.to_dict() for o in opps]), 200


@app.route('/api/opportunities', methods=['POST'])
def create_opportunity():
    admin = get_current_admin()
    if not admin:
        return jsonify({'error': 'Not authenticated'}), 401

    data            = request.get_json()
    required_fields = ['name', 'duration', 'start_date', 'description', 'skills', 'category', 'future_opps']

    for field in required_fields:
        if not (data.get(field) or '').strip():
            return jsonify({'error': f'{field} is required'}), 400

    opp = Opportunity(
        admin_id       = admin.id,
        name           = data['name'].strip(),
        duration       = data['duration'].strip(),
        start_date     = data['start_date'].strip(),
        description    = data['description'].strip(),
        skills         = data['skills'].strip(),
        category       = data['category'].strip(),
        future_opps    = data['future_opps'].strip(),
        max_applicants = (data.get('max_applicants') or '').strip() or None
    )
    db.session.add(opp)
    db.session.commit()
    return jsonify(opp.to_dict()), 201


@app.route('/api/opportunities/<int:opp_id>', methods=['PUT'])
def update_opportunity(opp_id):
    admin = get_current_admin()
    if not admin:
        return jsonify({'error': 'Not authenticated'}), 401

    opp = Opportunity.query.get_or_404(opp_id)
    if opp.admin_id != admin.id:
        return jsonify({'error': 'Forbidden'}), 403

    data            = request.get_json()
    required_fields = ['name', 'duration', 'start_date', 'description', 'skills', 'category', 'future_opps']

    for field in required_fields:
        if not (data.get(field) or '').strip():
            return jsonify({'error': f'{field} is required'}), 400

    opp.name           = data['name'].strip()
    opp.duration       = data['duration'].strip()
    opp.start_date     = data['start_date'].strip()
    opp.description    = data['description'].strip()
    opp.skills         = data['skills'].strip()
    opp.category       = data['category'].strip()
    opp.future_opps    = data['future_opps'].strip()
    opp.max_applicants = (data.get('max_applicants') or '').strip() or None
    db.session.commit()
    return jsonify(opp.to_dict()), 200


@app.route('/api/opportunities/<int:opp_id>', methods=['DELETE'])
def delete_opportunity(opp_id):
    admin = get_current_admin()
    if not admin:
        return jsonify({'error': 'Not authenticated'}), 401

    opp = Opportunity.query.get_or_404(opp_id)
    if opp.admin_id != admin.id:
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
