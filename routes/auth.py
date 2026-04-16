"""
Rutas de Autenticación - Login, Registro, Logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

# ─── Login ───────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email    = data.get('email', '').strip()
        password = data.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            if request.is_json:
                return jsonify({'success': True, 'user': user.to_dict(),
                                'redirect': url_for('main.home')})
            return redirect(url_for('main.home'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401
            flash('Email o contraseña incorrectos.', 'error')

    return render_template('auth/login.html')


# ─── Registro ────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        data   = request.get_json() if request.is_json else request.form
        nombre = data.get('nombre', '').strip()
        email  = data.get('email', '').strip()
        pwd    = data.get('password', '')

        if not nombre or not email or not pwd:
            msg = 'Todos los campos son obligatorios.'
            return (jsonify({'success': False, 'message': msg}), 400) if request.is_json else (flash(msg, 'error'), render_template('auth/register.html'))[1]

        if User.query.filter_by(email=email).first():
            msg = 'Este email ya está registrado.'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
            return render_template('auth/register.html')

        seed = nombre.replace(' ', '+')
        avatar = f'https://api.dicebear.com/7.x/avataaars/svg?seed={seed}'
        new_user = User(
            nombre=nombre,
            email=email,
            password=generate_password_hash(pwd),
            rol='user',
            avatar=avatar
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        if request.is_json:
            return jsonify({'success': True, 'user': new_user.to_dict(),
                            'redirect': url_for('main.home')})
        return redirect(url_for('main.home'))

    return render_template('auth/register.html')


# ─── Logout ──────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
