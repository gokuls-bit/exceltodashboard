import os
from flask import Flask
from database.models import db
# Each 'route' is like a specialized room in our clubhouse
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.income import income_bp
from routes.expense import expense_bp
from routes.budget import budget_bp
from routes.savings import savings_bp
from routes.reports import reports_bp    
from routes.export import export_bp

def create_app():
    # 1. Start building the foundation
    app = Flask(__name__)
    app.secret_key = "student-finance-key-1337" # The secret code for our clubhouse lock
    
    # 2. Setup the "Memory Bank" (Database)
    # We make sure the folder exists so we don't lose our notes!
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'finance.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # 3. Add the rooms (Blueprints)
    # Think of these as adding kitchen, bedroom, and study rooms to the house.
    blueprints = [
        auth_bp, dashboard_bp, income_bp, expense_bp, 
        budget_bp, savings_bp, reports_bp, export_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)
    
    # 4. Final inspection & Renovations
    with app.app_context():
        db.create_all() # Make sure all the cabinets are built
        
        # Checking if we need to add a new "Premium shelf" to our cabinet
        check_and_upgrade_database(db)
            
    return app

def check_and_upgrade_database(db):
    """Checks if our storage cabinet needs a new shelf (column)."""
    try:
        db.session.execute(db.text("SELECT is_premium FROM settings LIMIT 1"))
    except Exception:
        db.session.rollback()
        try:
            db.session.execute(db.text("ALTER TABLE settings ADD COLUMN is_premium BOOLEAN DEFAULT 0 NOT NULL"))
            db.session.commit()
            print("Successfully added the 'Premium' shelf to the cabinet!")
        except Exception as e:
            print(f"Could not add the shelf: {e}")

# The Clubhouse is ready!
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
