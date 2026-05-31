from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.models import db, Budget, Expense, Settings
from datetime import datetime, date
from sqlalchemy import extract, func

budget_bp = Blueprint('budget', __name__)

def get_current_settings():
    user_id = session.get('user_id')
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings

@budget_bp.route('/budget', methods=['GET'])
def list_budget():
    settings = get_current_settings()
    user_id = session['user_id']
    
    # Get active month filter, defaults to current month YYYY-MM
    selected_month = request.args.get('month', date.today().strftime('%Y-%m'))
    
    try:
        year_val, month_val = map(int, selected_month.split('-'))
    except ValueError:
        selected_month = date.today().strftime('%Y-%m')
        year_val = date.today().year
        month_val = date.today().month

    # Get budgets for selected month
    budgets = Budget.query.filter(Budget.month == selected_month, Budget.user_id == user_id).all()
    
    budget_details = []
    total_budget_limit = 0.0
    total_spent = 0.0
    
    for b in budgets:
        # Calculate actual spending in this category for this month and user
        spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.category == b.category,
            Expense.user_id == user_id,
            extract('year', Expense.date) == year_val,
            extract('month', Expense.date) == month_val
        ).scalar() or 0.0
        
        utilization = round((spent / b.limit_amount) * 100, 1) if b.limit_amount > 0 else 0.0
        remaining = b.limit_amount - spent
        is_overspent = spent > b.limit_amount
        
        budget_details.append({
            'id': b.id,
            'category': b.category,
            'limit_amount': b.limit_amount,
            'spent': spent,
            'remaining': remaining,
            'utilization': utilization,
            'is_overspent': is_overspent
        })
        
        total_budget_limit += b.limit_amount
        total_spent += spent

    # Available categories for selection
    categories = ["Food", "Transport", "Rent", "Education", "Books", "Shopping", "Entertainment", "Health", "Travel", "Subscriptions", "Other"]
    
    remaining_total = total_budget_limit - total_spent
    total_utilization = round((total_spent / total_budget_limit) * 100, 1) if total_budget_limit > 0 else 0.0
    
    return render_template(
        'budget.html',
        settings=settings,
        budgets=budget_details,
        categories=categories,
        selected_month=selected_month,
        total_budget_limit=total_budget_limit,
        total_spent=total_spent,
        remaining_total=remaining_total,
        total_utilization=total_utilization
    )

@budget_bp.route('/budget/add', methods=['POST'])
def add_budget():
    user_id = session['user_id']
    month = request.form.get('month')
    try:
        category = request.form.get('category')
        limit_amount_str = request.form.get('limit_amount')
        
        if not category or not limit_amount_str or not month:
            flash("All fields are required.", "danger")
            return redirect(url_for('budget.list_budget'))
            
        limit_amount = float(limit_amount_str)
        
        # Check if budget already exists for this category and month and user
        existing_budget = Budget.query.filter(
            Budget.category == category,
            Budget.month == month,
            Budget.user_id == user_id
        ).first()
        
        if existing_budget:
            flash(f"Budget for {category} in {month} already exists. You can edit it from the list.", "warning")
            return redirect(url_for('budget.list_budget', month=month))
            
        new_budget = Budget(category=category, limit_amount=limit_amount, month=month, user_id=user_id)
        db.session.add(new_budget)
        db.session.commit()
        
        flash("Budget limit set successfully!", "success")
    except ValueError as e:
        flash(f"Invalid budget limit value: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(url_for('budget.list_budget', month=month))

@budget_bp.route('/budget/edit/<int:id>', methods=['POST'])
def edit_budget(id):
    budget = Budget.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        limit_amount_str = request.form.get('limit_amount')
        
        if not limit_amount_str:
            flash("Limit amount is required.", "danger")
            return redirect(url_for('budget.list_budget', month=budget.month))
            
        budget.limit_amount = float(limit_amount_str)
        db.session.commit()
        flash("Budget limit updated successfully!", "success")
    except ValueError as e:
        flash(f"Invalid budget limit value: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(url_for('budget.list_budget', month=budget.month))

@budget_bp.route('/budget/delete/<int:id>', methods=['POST'])
def delete_budget(id):
    budget = Budget.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    month = budget.month
    try:
        db.session.delete(budget)
        db.session.commit()
        flash("Budget limit deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(url_for('budget.list_budget', month=month))
