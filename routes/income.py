from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from database.models import db, Income, Settings
from datetime import datetime

income_bp = Blueprint('income', __name__)

def get_current_settings():
    user_id = session.get('user_id')
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings

@income_bp.route('/income', methods=['GET'])
def list_income():
    settings = get_current_settings()
    
    # Filtering parameters
    search_query = request.args.get('search', '')
    source_filter = request.args.get('source', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    query = Income.query.filter_by(user_id=session['user_id'])
    
    if search_query:
        query = query.filter(Income.description.like(f"%{search_query}%") | Income.source.like(f"%{search_query}%"))
        
    if source_filter:
        query = query.filter(Income.source == source_filter)
        
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Income.date >= start_dt)
        except ValueError:
            pass
            
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Income.date <= end_dt)
        except ValueError:
            pass
            
    incomes = query.order_by(Income.date.desc(), Income.id.desc()).all()
    
    # List of valid sources for dropdown UI
    sources = ["Part-Time Income", "Freelancing", "Scholarship", "Pocket Money", "Internship Stipend", "Business Income", "Other Income"]
    
    return render_template(
        'income.html',
        incomes=incomes,
        sources=sources,
        settings=settings,
        search=search_query,
        selected_source=source_filter,
        start_date=start_date,
        end_date=end_date
    )

@income_bp.route('/income/add', methods=['POST'])
def add_income():
    try:
        date_str = request.form.get('date')
        source = request.form.get('source')
        amount_str = request.form.get('amount')
        description = request.form.get('description')
        
        if not date_str or not source or not amount_str:
            flash("All fields except description are required.", "danger")
            return redirect(request.referrer or url_for('income.list_income'))
            
        amount = float(amount_str)
        date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        new_income = Income(
            date=date_val,
            source=source,
            amount=amount,
            description=description,
            user_id=session['user_id']
        )
        db.session.add(new_income)
        db.session.commit()
        
        flash("Income record added successfully!", "success")
    except ValueError as e:
        flash(f"Invalid input values: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('income.list_income'))

@income_bp.route('/income/edit/<int:id>', methods=['POST'])
def edit_income(id):
    income = Income.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        date_str = request.form.get('date')
        source = request.form.get('source')
        amount_str = request.form.get('amount')
        description = request.form.get('description')
        
        if not date_str or not source or not amount_str:
            flash("All fields are required.", "danger")
            return redirect(request.referrer or url_for('income.list_income'))
            
        income.amount = float(amount_str)
        income.source = source
        income.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        income.description = description
        
        db.session.commit()
        flash("Income record updated successfully!", "success")
    except ValueError as e:
        flash(f"Invalid input values: {str(e)}", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('income.list_income'))

@income_bp.route('/income/delete/<int:id>', methods=['POST'])
def delete_income(id):
    income = Income.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    try:
        db.session.delete(income)
        db.session.commit()
        flash("Income record deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        
    return redirect(request.referrer or url_for('income.list_income'))
