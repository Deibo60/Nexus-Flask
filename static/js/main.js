/* ============================================================
   NEXUS MARKETPLACE — main.js
   Cart · Toasts · Theme · Fetch helpers
   ============================================================ */

// ── THEME ────────────────────────────────────────────────────
const savedTheme = localStorage.getItem('nexus-theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next    = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('nexus-theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('theme-icon');
  if (!icon) return;
  icon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
  if (window.lucide) lucide.createIcons();
}

// ── MOBILE MENU ──────────────────────────────────────────────
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  menu.classList.toggle('open');
}

// ── TOAST SYSTEM ─────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  const icons = { success:'✅', error:'❌', warning:'⚠️', info:'ℹ️' };

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || '•'}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('hide');
    setTimeout(() => toast.remove(), 350);
  }, duration);
}

// ── CART SYSTEM ──────────────────────────────────────────────
function toggleCart() {
  const sidebar = document.getElementById('cart-sidebar');
  const overlay = document.getElementById('cart-overlay');
  const isOpen  = sidebar.classList.contains('open');

  if (isOpen) {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
  } else {
    sidebar.classList.add('open');
    overlay.classList.add('active');
    loadCart();
  }
}

async function loadCart() {
  try {
    const res  = await fetch('/api/carrito');
    if (!res.ok) { updateCartUI([], 0); return; }
    const data = await res.json();
    updateCartUI(data.items, data.total);
  } catch (e) {
    updateCartUI([], 0);
  }
}

function updateCartUI(items, total) {
  const list  = document.getElementById('cart-items-list');
  const count = document.getElementById('cart-count');
  const price = document.getElementById('cart-total-price');

  count.textContent = items.length;
  price.textContent = `$${(total || 0).toLocaleString('es-MX', {minimumFractionDigits:2})}`;

  if (!items.length) {
    list.innerHTML = '<p class="cart-empty">😶 Tu carrito está vacío</p>';
    return;
  }

  list.innerHTML = items.map(item => `
    <div class="cart-item" id="cart-item-${item.id}">
      <img src="${item.imagen || 'https://via.placeholder.com/60'}" alt="${item.nombre}"/>
      <div class="cart-item-info">
        <p>${item.nombre}</p>
        <span class="cart-item-price">$${item.precio.toLocaleString('es-MX')} × ${item.cantidad}</span>
      </div>
      <button class="btn-icon-sm danger" onclick="removeCartItem(${item.id})" title="Eliminar">
        <i data-lucide="trash-2" style="width:14px;height:14px"></i>
      </button>
    </div>
  `).join('');
  if (window.lucide) lucide.createIcons();
}

async function addToCart(productId, productName) {
  try {
    const res = await fetch('/api/carrito', {
      method:  'POST',
      headers: {'Content-Type': 'application/json'},
      body:    JSON.stringify({ producto_id: productId, cantidad: 1 })
    });
    if (res.ok) {
      showToast(`${productName} agregado al carrito 🛒`, 'success');
      updateCartCount();
    } else {
      showToast('Inicia sesión para agregar al carrito', 'warning');
    }
  } catch {
    showToast('Error de conexión', 'error');
  }
}

async function removeCartItem(itemId) {
  await fetch(`/api/carrito/${itemId}`, { method: 'DELETE' });
  loadCart();
  showToast('Item eliminado', 'warning');
}

async function updateCartCount() {
  try {
    const res  = await fetch('/api/carrito');
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById('cart-count').textContent = data.items.length;
  } catch {}
}

async function checkout() {
  const res  = await fetch('/api/ordenes', { method: 'POST' });
  const data = await res.json();
  if (res.ok) {
    showToast('¡Orden creada exitosamente! 🎉', 'success');
    toggleCart();
    updateCartCount();
  } else {
    showToast(data.error || 'Error al crear la orden', 'error');
  }
}

// ── LIKE POSTS ───────────────────────────────────────────────
async function likePost(postId, btn) {
  const res  = await fetch(`/api/publicaciones/${postId}/like`, { method: 'POST' });
  const data = await res.json();
  const countEl = btn.querySelector('span');
  if (countEl) countEl.textContent = data.likes;
  btn.classList.toggle('liked');
}

// ── NAVBAR SCROLL EFFECT ─────────────────────────────────────
window.addEventListener('scroll', () => {
  const nav = document.getElementById('main-nav');
  if (!nav) return;
  nav.style.background = window.scrollY > 60
    ? (document.documentElement.getAttribute('data-theme') === 'dark'
        ? 'rgba(10,10,15,0.95)' : 'rgba(245,245,250,0.95)')
    : '';
});

// ── INTERSECTION OBSERVER (Animate on scroll) ─────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.08 });

document.querySelectorAll('.product-card, .stat-card, .feed-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// ── INIT ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateCartCount();
});
