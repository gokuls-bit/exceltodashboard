from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.models import db, SavingsGoal, Settings
from datetime import datetime

savings_bp = Blueprint('savings', __name__)

def get_current_settings():
    user_id = session.get('user_id')
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings

@savings_bp.route('/savings', methods=['GET'])
def list_savings():
    settings = get_current_settings()
    user_id = session['user_id']
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.id.desc()).all()
    
    # Calculate summary metrics
    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    total_progress_pct = round((total_saved / total_target * 100), 1) if total_target > 0 else 0.0
    
    # Standard categories
    standard_goals = ["Laptop Purchase", "Emergency Fund", "Certification Fund", "Study Abroad", "Startup Fund", "Vacation Fund"]

    return render_template(
        'savings.html',
        settings=settings,
        goals=goals,
        total_target=total_target,
        total_saved=total_saved,
        total_progress_pct=total_progress_pct,
        standard_goals=standard_goals
    )

@savings_bp.route('/savings/add', methods=['POST'])
def add_savings_goal():
    user_id = session['user_id']
    try:
        name = request.form.get('name')
        target_amount_str = request.form.get('target_amount')
        current_amount_str = request.form.get('current_amount', '0')
        target_date_str = request.form.get('target_date')
        
        if not name or not target_amount_str:
            flash("Goal Name and Target Amount are required.", "danger")
            return redirect(url_for('savings.list_savings'))
            
        target_amount = float(target_amount_str)
        current_amount = float(current_amount_str) if current_amount_str else 0.0
        
        target_date = None
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            
        new_goal = SavingsGoal(
            name=name,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            user_id=user_id
        )
        db.session.add(new_goal)
        db.session.commit()
        
        flash("Savings Goal created successfully!", "success")
    except ValueError as e:
        flash(f"Invalid numeric or date values: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(url_for('savings.list_savings'))

@savings_bp.route('/savings/edit/<int:id>', methods=['POST'])
def edit_savings_goal(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        name = request.form.get('name')
        target_amount_str = request.form.get('target_amount')
        current_amount_str = request.form.get('current_amount')
        target_date_str = request.form.get('target_date')
        
        if not name or not target_amount_str or not current_amount_str:
            flash("All fields are required.", "danger")
            return redirect(url_for('savings.list_savings'))
            
        goal.name = name
        goal.target_amount = float(target_amount_str)
        goal.current_amount = float(current_amount_str)
        
        if target_date_str:
            goal.target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            goal.target_date = None
            
        db.session.commit()
        flash("Savings Goal updated successfully!", "success")
    except ValueError as e:
        flash(f"Invalid numeric or date values: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(url_for('savings.list_savings'))

@savings_bp.route('/savings/delete/<int:id>', methods=['POST'])
def delete_savings_goal(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        db.session.delete(goal)
        db.session.commit()
        flash("Savings Goal deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(url_for('savings.list_savings'))
