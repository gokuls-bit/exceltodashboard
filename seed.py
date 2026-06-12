import os
from datetime import date, timedelta
from app import create_app
from database.models import db, User, Income, Expense, Budget, SavingsGoal, Settings

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data to make it clean
        db.drop_all()
        db.create_all()
        print("Seeding database...")
        test_user = User(username='student', email='student@finflow.com')
        test_user.set_password('studentpass')
        db.session.add(test_user)
        db.session.flush() 
        settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=test_user.id)
        db.session.add(settings)
        savings_goals = [
            SavingsGoal(name="Laptop Purchase", target_amount=1200.0, current_amount=450.0, target_date=date(2026, 9, 30), user_id=test_user.id),
            SavingsGoal(name="Emergency Fund", target_amount=1500.0, current_amount=900.0, target_date=date(2026, 12, 31), user_id=test_user.id),
            SavingsGoal(name="Certification Fund", target_amount=300.0, current_amount=120.0, target_date=date(2026, 7, 15), user_id=test_user.id),
            SavingsGoal(name="Vacation Fund", target_amount=800.0, current_amount=0.0, target_date=date(2026, 8, 20), user_id=test_user.id)
        ]
        db.session.add_all(savings_goals)
        
        # 4. Monthly Budgets (Current Month YYYY-MM)
        current_month_str = date.today().strftime('%Y-%m')
        budgets = [
            Budget(category="Food", limit_amount=300.0, month=current_month_str, user_id=test_user.id),
            Budget(category="Transport", limit_amount=120.0, month=current_month_str, user_id=test_user.id),
            Budget(category="Rent", limit_amount=600.0, month=current_month_str, user_id=test_user.id),
            Budget(category="Entertainment", limit_amount=150.0, month=current_month_str, user_id=test_user.id),
            Budget(category="Shopping", limit_amount=200.0, month=current_month_str, user_id=test_user.id),
            Budget(category="Education", limit_amount=100.0, month=current_month_str, user_id=test_user.id)
        ]
        db.session.add_all(budgets)
        
        # 5. Incomes (Spread across last 4 months)
        today = date.today()
        incomes = [
            # Current Month
            Income(date=today - timedelta(days=2), source="Part-Time Income", amount=650.0, description="Bi-weekly library assistant stipend", user_id=test_user.id),
            Income(date=today - timedelta(days=12), source="Freelancing", amount=850.0, description="Website design contract", user_id=test_user.id),
            Income(date=today - timedelta(days=20), source="Scholarship", amount=400.0, description="Monthly academic excellence stipend", user_id=test_user.id),
            Income(date=today - timedelta(days=25), source="Pocket Money", amount=200.0, description="Monthly allowance", user_id=test_user.id),
            
            # Previous Month (Month - 1)
            Income(date=today - timedelta(days=32), source="Part-Time Income", amount=650.0, description="Library assistant paycheck", user_id=test_user.id),
            Income(date=today - timedelta(days=40), source="Freelancing", amount=500.0, description="Logo graphics design", user_id=test_user.id),
            Income(date=today - timedelta(days=50), source="Scholarship", amount=400.0, description="Monthly stipend", user_id=test_user.id),
            Income(date=today - timedelta(days=55), source="Pocket Money", amount=200.0, description="Monthly allowance", user_id=test_user.id),
            
            # Month - 2
            Income(date=today - timedelta(days=62), source="Part-Time Income", amount=600.0, description="Library work", user_id=test_user.id),
            Income(date=today - timedelta(days=70), source="Freelancing", amount=950.0, description="Mobile app backend development", user_id=test_user.id),
            Income(date=today - timedelta(days=80), source="Scholarship", amount=400.0, description="Monthly stipend", user_id=test_user.id),
            Income(date=today - timedelta(days=85), source="Pocket Money", amount=200.0, description="Monthly allowance", user_id=test_user.id),
            
            # Month - 3
            Income(date=today - timedelta(days=92), source="Part-Time Income", amount=600.0, description="Library work", user_id=test_user.id),
            Income(date=today - timedelta(days=110), source="Scholarship", amount=400.0, description="Monthly stipend", user_id=test_user.id),
            Income(date=today - timedelta(days=115), source="Pocket Money", amount=200.0, description="Monthly allowance", user_id=test_user.id)
        ]
        db.session.add_all(incomes)
        
        # 6. Expenses (Spread across last 4 months)
        expenses = [
            # Current Month
            Expense(date=today - timedelta(days=1), category="Food", amount=25.50, description="Groceries at Whole Foods", user_id=test_user.id),
            Expense(date=today - timedelta(days=3), category="Rent", amount=600.0, description="Monthly apartment shared rent", user_id=test_user.id),
            Expense(date=today - timedelta(days=5), category="Transport", amount=45.00, description="Train pass renewal", user_id=test_user.id),
            Expense(date=today - timedelta(days=8), category="Food", amount=12.20, description="Lunch at campus cafe", user_id=test_user.id),
            Expense(date=today - timedelta(days=10), category="Entertainment", amount=55.00, description="Concert tickets", user_id=test_user.id),
            Expense(date=today - timedelta(days=14), category="Books", amount=85.00, description="Algorithm engineering textbooks", user_id=test_user.id),
            Expense(date=today - timedelta(days=16), category="Shopping", amount=120.0, description="New winter jacket", user_id=test_user.id),
            Expense(date=today - timedelta(days=18), category="Subscriptions", amount=15.99, description="Netflix subscription", user_id=test_user.id),
            Expense(date=today - timedelta(days=22), category="Food", amount=32.40, description="Dinner with classmates", user_id=test_user.id),
            Expense(date=today - timedelta(days=24), category="Travel", amount=210.0, description="Weekend train ride home", user_id=test_user.id),
            
            # Previous Month (Month - 1)
            Expense(date=today - timedelta(days=31), category="Food", amount=18.50, description="Campus groceries", user_id=test_user.id),
            Expense(date=today - timedelta(days=33), category="Rent", amount=600.0, description="Monthly rent", user_id=test_user.id),
            Expense(date=today - timedelta(days=35), category="Transport", amount=45.00, description="Train pass", user_id=test_user.id),
            Expense(date=today - timedelta(days=38), category="Food", amount=38.40, description="Sushi night out", user_id=test_user.id),
            Expense(date=today - timedelta(days=42), category="Entertainment", amount=25.00, description="Movie and popcorn", user_id=test_user.id),
            Expense(date=today - timedelta(days=45), category="Shopping", amount=75.00, description="Clothes shopping", user_id=test_user.id),
            Expense(date=today - timedelta(days=48), category="Subscriptions", amount=15.99, description="Netflix subscription", user_id=test_user.id),
            Expense(date=today - timedelta(days=52), category="Health", amount=40.00, description="Pharmacy prescription", user_id=test_user.id),
            
            # Month - 2
            Expense(date=today - timedelta(days=63), category="Rent", amount=600.0, description="Monthly rent", user_id=test_user.id),
            Expense(date=today - timedelta(days=65), category="Transport", amount=45.00, description="Train pass", user_id=test_user.id),
            Expense(date=today - timedelta(days=68), category="Food", amount=42.00, description="Weekly grocery haul", user_id=test_user.id),
            Expense(date=today - timedelta(days=72), category="Entertainment", amount=70.00, description="Bowling & arcade tickets", user_id=test_user.id),
            Expense(date=today - timedelta(days=78), category="Subscriptions", amount=15.99, description="Netflix subscription", user_id=test_user.id),
            Expense(date=today - timedelta(days=82), category="Food", amount=28.50, description="Dinner at campus cafeteria", user_id=test_user.id),
            
            # Month - 3
            Expense(date=today - timedelta(days=93), category="Rent", amount=600.0, description="Monthly rent", user_id=test_user.id),
            Expense(date=today - timedelta(days=95), category="Transport", amount=45.00, description="Train pass", user_id=test_user.id),
            Expense(date=today - timedelta(days=98), category="Food", amount=35.00, description="Groceries", user_id=test_user.id),
            Expense(date=today - timedelta(days=105), category="Books", amount=110.0, description="Calculus & Physics reference books", user_id=test_user.id),
            Expense(date=today - timedelta(days=108), category="Subscriptions", amount=15.99, description="Netflix subscription", user_id=test_user.id)
        ]
        db.session.add_all(expenses)
        
        db.session.commit()
        print("Database successfully seeded with default user and mock data!")

if __name__ == "__main__":
    seed_database()
