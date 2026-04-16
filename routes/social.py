"""
Rutas de Red Social
"""
from flask import Blueprint, render_template
from flask_login import login_required
from models.post import Post

social_bp = Blueprint('social', __name__)

@social_bp.route('/')
def feed():
    posts = Post.query.order_by(Post.fecha.desc()).limit(20).all()
    return render_template('social/feed.html', posts=posts)
