"""
Rutas del Panel de Administración
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from models.product import Product
from models.post import Post, Order

admin_bp = Blueprint('admin', __name__)

def admin_only(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_only
def dashboard():
    stats = {
        'usuarios':      User.query.count(),
        'productos':     Product.query.filter_by(activo=True).count(),
        'publicaciones': Post.query.count(),
        'ordenes':       Order.query.count(),
        'revenue':       sum(o.total for o in Order.query.all())
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/usuarios')
@login_required
@admin_only
def usuarios():
    return render_template('admin/usuarios.html')

@admin_bp.route('/productos')
@login_required
@admin_only
def productos():
    return render_template('admin/productos.html')

@admin_bp.route('/publicaciones')
@login_required
@admin_only
def publicaciones():
    return render_template('admin/publicaciones.html')
