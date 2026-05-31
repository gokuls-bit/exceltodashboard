from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.models import db, User, Settings

auth_bp = Blueprint('auth', __name__)

@auth_bp.before_app_request
def require_login():
    # Public endpoints that do not require authentication
    allowed_endpoints = ['auth.login', 'auth.register', 'static']
    
    if request.endpoint and request.endpoint not in allowed_endpoints:
        if 'user_id' not in session:
            # Store the requested URL to redirect the user after login
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))

@auth_bp.app_context_processor
def inject_user_and_settings():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            # Ensure settings exist for the user (fail-safe)
            settings = Settings.query.filter_by(user_id=user.id).first()
            if not settings:
                settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=user.id)
                db.session.add(settings)
                db.session.commit()
            return dict(current_user=user, settings=settings)
    return dict(current_user=None, settings=None)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.home'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f"Welcome back, {user.username}!", "success")
            
            # Redirect to originally requested URL, if it exists
            next_url = session.pop('next_url', None)
            return redirect(next_url or url_for('dashboard.home'))
            
        flash("Invalid username or password.", "danger")
        return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.home'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('auth.register'))
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "danger")
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for('auth.register'))
            
        try:
            # Create user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush() # Get user ID before commit
            
            # Create user settings
            user_settings = Settings(
                currency='USD',
                theme='light',
                export_preference='excel',
                user_id=new_user.id
            )
            db.session.add(user_settings)
            db.session.commit()
            
            # Automatically log in the user
            session['user_id'] = new_user.id
            flash("Account registered successfully! Welcome to FinFlow.", "success")
            return redirect(url_for('dashboard.home'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred during registration: {str(e)}", "danger")
            return redirect(url_for('auth.register'))
            
    return render_template('register.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    session.pop('next_url', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('auth.login'))
