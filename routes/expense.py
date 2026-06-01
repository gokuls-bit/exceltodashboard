from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.models import db, Expense, Settings
from datetime import datetime

expense_bp = Blueprint('expense', __name__)

def get_current_settings():
    user_id = session.get('user_id')
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings

@expense_bp.route('/expense', methods=['GET'])
def list_expense():
    settings = get_current_settings()
    
    # Filter/Search parameters
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = Expense.query.filter_by(user_id=session['user_id'])
    
    if search_query:
        query = query.filter(Expense.description.like(f"%{search_query}%") | Expense.category.like(f"%{search_query}%"))
        
    if category_filter:
        query = query.filter(Expense.category == category_filter)
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= start_dt)
        except ValueError:
            pass
            
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= end_dt)
        except ValueError:
            pass
            
    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    
    # List of categories for dropdown UI
    categories = ["Food", "Transport", "Rent", "Education", "Books", "Shopping", "Entertainment", "Health", "Travel", "Subscriptions", "Other"]
    
    return render_template(
        'expense.html',
        expenses=expenses,
        categories=categories,
        settings=settings,
        search=search_query,
        selected_category=category_filter,
        start_date=start_date,
        end_date=end_date
    )

@expense_bp.route('/expense/add', methods=['POST'])
def add_expense():
    try:
        date_str = request.form.get('date')
        category = request.form.get('category')
        amount_str = request.form.get('amount')
        description = request.form.get('description')
        
        if not date_str or not category or not amount_str:
            flash("All fields except description are required.", "danger")
            return redirect(request.referrer or url_for('expense.list_expense'))
            
        amount = float(amount_str)
        date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        new_expense = Expense(
            date=date_val,
            category=category,
            amount=amount,
            description=description,
            user_id=session['user_id']
        )
        db.session.add(new_expense)
        db.session.commit()
        
        flash("Expense record added successfully!", "success")
    except ValueError as e:
        flash(f"Invalid input values: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('expense.list_expense'))

@expense_bp.route('/expense/edit/<int:id>', methods=['POST'])
def edit_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        date_str = request.form.get('date')
        category = request.form.get('category')
        amount_str = request.form.get('amount')
        description = request.form.get('description')
        
        if not date_str or not category or not amount_str:
            flash("All fields are required.", "danger")
            return redirect(request.referrer or url_for('expense.list_expense'))
            
        expense.amount = float(amount_str)
        expense.category = category
        expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        expense.description = description
        
        db.session.commit()
        flash("Expense record updated successfully!", "success")
    except ValueError as e:
        flash(f"Invalid input values: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('expense.list_expense'))

@expense_bp.route('/expense/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense record deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('expense.list_expense'))
