"""
API REST - Endpoints JSON (Protocolo de Comunicación)
GET/POST/PUT/DELETE para Productos, Usuarios, Publicaciones
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models.user import User
from models.product import Product
from models.post import Post, Comment, CartItem, Order
import json

api_bp = Blueprint('api', __name__)

def admin_required(f):
    """Decorador: solo admins."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol admin.'}), 403
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════════════════════════
#  PRODUCTOS
# ═══════════════════════════════════════════════════════════

@api_bp.route('/productos', methods=['GET'])
def get_productos():
    """GET /api/productos - Lista todos los productos."""
    cat  = request.args.get('categoria')
    q    = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    query = Product.query.filter_by(activo=True)
    if cat:
        query = query.filter_by(categoria=cat)
    if q:
        query = query.filter(Product.nombre.ilike(f'%{q}%'))

    productos = query.order_by(Product.fecha_crea.desc()).paginate(page=page, per_page=12)

    return jsonify({
        'productos':  [p.to_dict() for p in productos.items],
        'total':      productos.total,
        'pagina':     productos.page,
        'paginas':    productos.pages
    })

@api_bp.route('/productos/<int:pid>', methods=['GET'])
def get_producto(pid):
    """GET /api/productos/<id> - Obtiene un producto."""
    p = Product.query.get_or_404(pid)
    return jsonify(p.to_dict())

@api_bp.route('/productos', methods=['POST'])
@login_required
def create_producto():
    """POST /api/productos - Crea un nuevo producto."""
    data = request.get_json()
    if not data or not data.get('nombre') or not data.get('precio'):
        return jsonify({'error': 'nombre y precio son obligatorios'}), 400

    p = Product(
        nombre      = data['nombre'],
        precio      = float(data['precio']),
        descripcion = data.get('descripcion', ''),
        imagen      = data.get('imagen', 'https://via.placeholder.com/400'),
        categoria   = data.get('categoria', 'General'),
        stock       = int(data.get('stock', 10)),
        lat         = float(data.get('lat', 20.5204)),
        lng         = float(data.get('lng', -100.8147)),
        usuario_id  = current_user.id
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'Producto creado', 'producto': p.to_dict()}), 201

@api_bp.route('/productos/<int:pid>', methods=['PUT'])
@login_required
def update_producto(pid):
    """PUT /api/productos/<id> - Actualiza un producto."""
    p = Product.query.get_or_404(pid)
    if p.usuario_id != current_user.id and current_user.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403

    data = request.get_json()
    p.nombre      = data.get('nombre', p.nombre)
    p.precio      = float(data.get('precio', p.precio))
    p.descripcion = data.get('descripcion', p.descripcion)
    p.imagen      = data.get('imagen', p.imagen)
    p.categoria   = data.get('categoria', p.categoria)
    p.stock       = int(data.get('stock', p.stock))
    db.session.commit()
    return jsonify({'message': 'Producto actualizado', 'producto': p.to_dict()})

@api_bp.route('/productos/<int:pid>', methods=['DELETE'])
@login_required
def delete_producto(pid):
    """DELETE /api/productos/<id> - Elimina un producto."""
    p = Product.query.get_or_404(pid)
    if p.usuario_id != current_user.id and current_user.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    p.activo = False
    db.session.commit()
    return jsonify({'message': 'Producto eliminado'})

# ═══════════════════════════════════════════════════════════
#  USUARIOS
# ═══════════════════════════════════════════════════════════

@api_bp.route('/usuarios', methods=['GET'])
@login_required
@admin_required
def get_usuarios():
    """GET /api/usuarios - Lista usuarios (solo admin)."""
    usuarios = User.query.all()
    return jsonify({'usuarios': [u.to_dict() for u in usuarios]})

@api_bp.route('/usuarios/<int:uid>', methods=['GET'])
@login_required
def get_usuario(uid):
    """GET /api/usuarios/<id>"""
    u = User.query.get_or_404(uid)
    return jsonify(u.to_dict())

@api_bp.route('/usuarios', methods=['POST'])
@login_required
@admin_required
def create_usuario():
    """POST /api/usuarios - Crea usuario (solo admin)."""
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email ya registrado'}), 400

    u = User(
        nombre   = data['nombre'],
        email    = data['email'],
        password = generate_password_hash(data.get('password', 'nexus123')),
        rol      = data.get('rol', 'user'),
        avatar   = f"https://api.dicebear.com/7.x/avataaars/svg?seed={data['nombre']}"
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({'message': 'Usuario creado', 'usuario': u.to_dict()}), 201

@api_bp.route('/usuarios/<int:uid>', methods=['PUT'])
@login_required
def update_usuario(uid):
    """PUT /api/usuarios/<id>"""
    if current_user.id != uid and current_user.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403

    u    = User.query.get_or_404(uid)
    data = request.get_json()
    u.nombre = data.get('nombre', u.nombre)
    u.bio    = data.get('bio', u.bio)
    if current_user.rol == 'admin':
        u.rol    = data.get('rol', u.rol)
        u.activo = data.get('activo', u.activo)
    db.session.commit()
    return jsonify({'message': 'Usuario actualizado', 'usuario': u.to_dict()})

@api_bp.route('/usuarios/<int:uid>', methods=['DELETE'])
@login_required
@admin_required
def delete_usuario(uid):
    """DELETE /api/usuarios/<id> (solo admin)."""
    u = User.query.get_or_404(uid)
    u.activo = False
    db.session.commit()
    return jsonify({'message': 'Usuario desactivado'})

# ═══════════════════════════════════════════════════════════
#  PUBLICACIONES
# ═══════════════════════════════════════════════════════════

@api_bp.route('/publicaciones', methods=['GET'])
def get_publicaciones():
    """GET /api/publicaciones - Feed social."""
    page  = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.fecha.desc()).paginate(page=page, per_page=10)
    return jsonify({
        'publicaciones': [p.to_dict() for p in posts.items],
        'total':         posts.total,
        'paginas':       posts.pages
    })

@api_bp.route('/publicaciones', methods=['POST'])
@login_required
def create_publicacion():
    """POST /api/publicaciones - Crear post."""
    data = request.get_json()
    if not data or not data.get('contenido'):
        return jsonify({'error': 'contenido obligatorio'}), 400

    p = Post(
        contenido  = data['contenido'],
        imagen     = data.get('imagen'),
        usuario_id = current_user.id
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'Publicación creada', 'publicacion': p.to_dict()}), 201

@api_bp.route('/publicaciones/<int:pid>', methods=['DELETE'])
@login_required
def delete_publicacion(pid):
    p = Post.query.get_or_404(pid)
    if p.usuario_id != current_user.id and current_user.rol != 'admin':
        return jsonify({'error': 'Sin permisos'}), 403
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Publicación eliminada'})

@api_bp.route('/publicaciones/<int:pid>/like', methods=['POST'])
def like_post(pid):
    """POST /api/publicaciones/<id>/like - Dar like."""
    p = Post.query.get_or_404(pid)
    p.likes += 1
    db.session.commit()
    return jsonify({'likes': p.likes})

@api_bp.route('/publicaciones/<int:pid>/comentarios', methods=['GET', 'POST'])
def comentarios(pid):
    """GET/POST comentarios de una publicación."""
    p = Post.query.get_or_404(pid)
    if request.method == 'GET':
        return jsonify({'comentarios': [c.to_dict() for c in p.comentarios]})

    if not current_user.is_authenticated:
        return jsonify({'error': 'Debes iniciar sesión'}), 401

    data = request.get_json()
    c = Comment(contenido=data['contenido'], usuario_id=current_user.id, publicacion_id=pid)
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'Comentario agregado', 'comentario': c.to_dict()}), 201

# ═══════════════════════════════════════════════════════════
#  CARRITO Y ÓRDENES
# ═══════════════════════════════════════════════════════════

@api_bp.route('/carrito', methods=['GET'])
@login_required
def get_carrito():
    items = CartItem.query.filter_by(usuario_id=current_user.id).all()
    total = sum(i.producto.precio * i.cantidad for i in items if i.producto)
    return jsonify({'items': [i.to_dict() for i in items], 'total': total})

@api_bp.route('/carrito', methods=['POST'])
@login_required
def add_carrito():
    data       = request.get_json()
    prod_id    = data.get('producto_id')
    cantidad   = int(data.get('cantidad', 1))
    existing   = CartItem.query.filter_by(usuario_id=current_user.id, producto_id=prod_id).first()
    if existing:
        existing.cantidad += cantidad
    else:
        item = CartItem(usuario_id=current_user.id, producto_id=prod_id, cantidad=cantidad)
        db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Producto agregado al carrito'})

@api_bp.route('/carrito/<int:item_id>', methods=['DELETE'])
@login_required
def remove_carrito(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.usuario_id != current_user.id:
        return jsonify({'error': 'Sin permisos'}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item eliminado del carrito'})

@api_bp.route('/ordenes', methods=['POST'])
@login_required
def create_orden():
    items = CartItem.query.filter_by(usuario_id=current_user.id).all()
    if not items:
        return jsonify({'error': 'El carrito está vacío'}), 400

    total    = sum(i.producto.precio * i.cantidad for i in items if i.producto)
    detalles = json.dumps([i.to_dict() for i in items])
    orden    = Order(usuario_id=current_user.id, total=total, detalles=detalles)
    db.session.add(orden)

    for item in items:
        db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Orden creada', 'orden': orden.to_dict()}), 201

@api_bp.route('/ordenes', methods=['GET'])
@login_required
def get_ordenes():
    ordenes = Order.query.filter_by(usuario_id=current_user.id).order_by(Order.fecha.desc()).all()
    return jsonify({'ordenes': [o.to_dict() for o in ordenes]})

# ─── Stats para admin ────────────────────────────────────────
@api_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def get_stats():
    return jsonify({
        'usuarios':     User.query.count(),
        'productos':    Product.query.filter_by(activo=True).count(),
        'publicaciones':Post.query.count(),
        'ordenes':      Order.query.count(),
        'revenue':      sum(o.total for o in Order.query.all())
    })
