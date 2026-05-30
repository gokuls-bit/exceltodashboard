from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Income(db.Model):
    __tablename__ = 'income'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(100), nullable=False)  # Part-Time Income, Freelancing, Scholarship, Pocket Money, Internship Stipend, Business Income, Other Income
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'source': self.source,
            'amount': self.amount,
            'description': self.description or ''
        }

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=False)  # Food, Transport, Rent, Education, Books, Shopping, Entertainment, Health, Travel, Subscriptions, Other
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'category': self.category,
            'amount': self.amount,
            'description': self.description or ''
        }

class Budget(db.Model):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # Food, Travel, Education, Entertainment, Shopping, Health, Custom Categories
    limit_amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM (e.g. 2026-05)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'limit_amount': self.limit_amount,
            'month': self.month
        }

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goal'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Laptop Purchase, Emergency Fund, Certification Fund, Study Abroad, Startup Fund, Vacation Fund, etc.
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.0)
    target_date = db.Column(db.Date, nullable=True)  # Expected Completion

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'progress_percent': round((self.current_amount / self.target_amount) * 100, 1) if self.target_amount > 0 else 0
        }

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    theme = db.Column(db.String(10), nullable=False, default='light')
    export_preference = db.Column(db.String(20), nullable=False, default='excel')

    def to_dict(self):
        return {
            'id': self.id,
            'currency': self.currency,
            'theme': self.theme,
            'export_preference': self.export_preference
        }
