"""
Rutas de E-Commerce
"""
from flask import Blueprint, render_template
from models.product import Product

ecommerce_bp = Blueprint('ecommerce', __name__)

@ecommerce_bp.route('/')
def catalogo():
    categorias = ['Tecnología','Audio','Fotografía','Drones','General']
    productos  = Product.query.filter_by(activo=True).order_by(Product.fecha_crea.desc()).all()
    return render_template('ecommerce/catalogo.html',
                           productos=productos, categorias=categorias)

@ecommerce_bp.route('/carrito')
def carrito():
    return render_template('ecommerce/carrito.html')
