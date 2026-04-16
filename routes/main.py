"""
Rutas Principales - Home y Dashboard de Usuario
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.product import Product
from models.post import Post, Comment
from models.user import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    productos = Product.query.filter_by(activo=True).order_by(Product.fecha_crea.desc()).limit(6).all()
    posts     = Post.query.order_by(Post.fecha.desc()).limit(10).all()
    return render_template('main/home.html', productos=productos, posts=posts)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol == 'admin':
        return redirect(url_for('admin.dashboard'))
    mis_posts     = Post.query.filter_by(usuario_id=current_user.id).all()
    mis_productos = Product.query.filter_by(usuario_id=current_user.id).all()
    return render_template('main/user_dashboard.html',
                           mis_posts=mis_posts, mis_productos=mis_productos)

@main_bp.route('/perfil')
@login_required
def perfil():
    return render_template('main/perfil.html')
