import os
from flask import Flask, redirect, url_for
from database.models import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.income import income_bp
from routes.expense import expense_bp
from routes.budget import budget_bp
from routes.savings import savings_bp
from routes.reports import reports_bp
from routes.export import export_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "student-finance-key-1337"
    
    # Configure SQLite database in instance folder
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'finance.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(export_bp)
    
    with app.app_context():
        db.create_all()
            
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
