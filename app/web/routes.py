from flask import render_template
from . import web
from app.models.items import LaundryItem

@web.route('/')
def index():
    return render_template('landing.html')



@web.route('/pricing')
def pricing():
    items = LaundryItem.query.all()
    categories = {}
    for item in items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)
    return render_template('pricing.html', categories=categories)

@web.route('/services')
def services():
    return render_template('services.html')

@web.route('/about')
def about():
    return render_template('about.html')

@web.route('/help')
def help():
    return render_template('help.html')

@web.route('/login')
def login():
    return render_template('auth/login.html')

@web.route('/register')
def register():
    return render_template('auth/register.html')

@web.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')

@web.route('/reset-password/<token>')
def reset_password_page(token):
    return render_template('auth/reset_password.html', token=token) # Pass token to template if needed, or JS extracts it

@web.route('/dashboard')
def dashboard():
    return render_template('customer/dashboard.html')

@web.route('/create-order')
def create_order():
    return render_template('customer/create_order.html')

@web.route('/rider/dashboard')
def rider_dashboard():
    return render_template('rider/dashboard.html')

@web.route('/staff/dashboard')
def staff_dashboard():
    return render_template('staff/dashboard.html')

@web.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@web.route('/admin/items')
def admin_items():
    return render_template('admin/items.html')

@web.route('/admin/users')
def admin_users():
    return render_template('admin/users.html')

@web.route('/admin/orders')
def admin_orders():
    return render_template('admin/orders.html')

@web.route('/admin/settings')
def admin_settings():
    return render_template('admin/settings.html')

@web.route('/admin/finance')
def admin_finance():
    return render_template('admin/finance.html')
