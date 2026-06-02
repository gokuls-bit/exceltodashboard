from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, send_file, current_app, session
from database.models import db, Income, Expense, Budget, SavingsGoal, Settings
from datetime import datetime, date
from sqlalchemy import extract, func
import os
import json
import io

dashboard_bp = Blueprint('dashboard', __name__)

def get_current_settings():
    user_id = session.get('user_id')
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = Settings(currency='USD', theme='light', export_preference='excel', user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings

def get_financial_score(income_val, expense_val, savings_val, budget_val, actual_budget_spent):
    # Financial Score calculation logic:
    # 1. Savings Rate Score (max 30 points)
    # 2. Expense Ratio Score (max 30 points)
    # 3. Budget Adherence Score (max 40 points)
    
    savings_rate = (savings_val / income_val) * 100 if income_val > 0 else 0
    expense_ratio = (expense_val / income_val) * 100 if income_val > 0 else 0
    
    # Savings rate score
    if savings_rate >= 30:
        savings_score = 30
    elif savings_rate >= 20:
        savings_score = 25
    elif savings_rate >= 10:
        savings_score = 15
    elif savings_rate > 0:
        savings_score = 10
    else:
        savings_score = 0

    # Expense ratio score
    if expense_ratio <= 40:
        expense_score = 30
    elif expense_ratio <= 60:
        expense_score = 25
    elif expense_ratio <= 80:
        expense_score = 15
    elif expense_ratio <= 100:
        expense_score = 10
    else:
        expense_score = 0

    # Budget adherence score
    if budget_val > 0:
        overspend = max(0, actual_budget_spent - budget_val)
        adherence_pct = max(0, 1 - (overspend / budget_val))
        budget_score = adherence_pct * 40
    else:
        budget_score = 40  # Default full score if no budget limit is set

    total_score = round(savings_score + expense_score + budget_score)
    
    if total_score >= 80:
        status = "Excellent"
    elif total_score >= 60:
        status = "Good"
    elif total_score >= 40:
        status = "Average"
    else:
        status = "Poor"
        
    return total_score, status

@dashboard_bp.route('/')
def home():
    settings = get_current_settings()
    user_id = session['user_id']
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    curr_month_str = today.strftime('%Y-%m')
    
    # Calculate Total Incomes & Expenses (User specific)
    total_income = db.session.query(func.sum(Income.amount)).filter(Income.user_id == user_id).scalar() or 0.0
    total_expense = db.session.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id).scalar() or 0.0
    current_balance = total_income - total_expense
    
    # Current Month metrics
    current_month_income = db.session.query(func.sum(Income.amount))\
        .filter(Income.user_id == user_id, extract('year', Income.date) == current_year, extract('month', Income.date) == current_month).scalar() or 0.0
    current_month_expense = db.session.query(func.sum(Expense.amount))\
        .filter(Expense.user_id == user_id, extract('year', Expense.date) == current_year, extract('month', Expense.date) == current_month).scalar() or 0.0
        
    # Previous Month metrics (for trend)
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    
    prev_month_income = db.session.query(func.sum(Income.amount))\
        .filter(Income.user_id == user_id, extract('year', Income.date) == prev_year, extract('month', Income.date) == prev_month).scalar() or 0.0
    prev_month_expense = db.session.query(func.sum(Expense.amount))\
        .filter(Expense.user_id == user_id, extract('year', Expense.date) == prev_year, extract('month', Expense.date) == prev_month).scalar() or 0.0
        
    # Calculate Trends (percentage growth)
    income_trend = 0.0
    if prev_month_income > 0:
        income_trend = ((current_month_income - prev_month_income) / prev_month_income) * 100
        
    expense_trend = 0.0
    if prev_month_expense > 0:
        expense_trend = ((current_month_expense - prev_month_expense) / prev_month_expense) * 100
        
    # Budget Planner Metrics
    total_budget_limit = db.session.query(func.sum(Budget.limit_amount))\
        .filter(Budget.user_id == user_id, Budget.month == curr_month_str).scalar() or 0.0
        
    budgets = Budget.query.filter(Budget.user_id == user_id, Budget.month == curr_month_str).all()
    budgeted_categories = [b.category for b in budgets]
    
    actual_budgeted_spent = 0.0
    if budgeted_categories:
        actual_budgeted_spent = db.session.query(func.sum(Expense.amount))\
            .filter(
                Expense.user_id == user_id,
                extract('year', Expense.date) == current_year,
                extract('month', Expense.date) == current_month,
                Expense.category.in_(budgeted_categories)
            ).scalar() or 0.0
            
    remaining_budget = total_budget_limit - actual_budgeted_spent
    
    # Savings Goals Metrics
    current_savings = db.session.query(func.sum(SavingsGoal.current_amount)).filter(SavingsGoal.user_id == user_id).scalar() or 0.0
    target_savings = db.session.query(func.sum(SavingsGoal.target_amount)).filter(SavingsGoal.user_id == user_id).scalar() or 0.0
    savings_progress_pct = round((current_savings / target_savings * 100), 1) if target_savings > 0 else 0.0
    
    # Financial Score
    financial_score, financial_quality = get_financial_score(
        current_month_income,
        current_month_expense,
        current_savings,
        total_budget_limit,
        actual_budgeted_spent
    )
    
    # Recent Transactions
    incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc(), Income.id.desc()).limit(5).all()
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc(), Expense.id.desc()).limit(5).all()
    
    recent_transactions = []
    for inc in incomes:
        recent_transactions.append({
            'id': inc.id,
            'type': 'Income',
            'date': inc.date,
            'category_or_source': inc.source,
            'amount': inc.amount,
            'description': inc.description or ''
        })
    for exp in expenses:
        recent_transactions.append({
            'id': exp.id,
            'type': 'Expense',
            'date': exp.date,
            'category_or_source': exp.category,
            'amount': exp.amount,
            'description': exp.description or ''
        })
        
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:5]
    
    return render_template(
        'dashboard.html',
        settings=settings,
        current_balance=current_balance,
        total_income=total_income,
        total_expense=total_expense,
        current_month_income=current_month_income,
        current_month_expense=current_month_expense,
        income_trend=round(income_trend, 1),
        expense_trend=round(expense_trend, 1),
        total_budget_limit=total_budget_limit,
        remaining_budget=remaining_budget,
        actual_budgeted_spent=actual_budgeted_spent,
        current_savings=current_savings,
        target_savings=target_savings,
        savings_progress_pct=savings_progress_pct,
        financial_score=financial_score,
        financial_quality=financial_quality,
        recent_transactions=recent_transactions
    )

@dashboard_bp.route('/api/charts/data')
def charts_data():
    today = date.today()
    current_year = today.year
    curr_month_str = today.strftime('%Y-%m')
    user_id = session['user_id']
    
    # 1. Cash Flow Chart: Monthly Income vs Expense (Current Year)
    months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_income = [0.0] * 12
    monthly_expense = [0.0] * 12
    
    incomes = db.session.query(
        extract('month', Income.date).label('month'),
        func.sum(Income.amount)
    ).filter(Income.user_id == user_id, extract('year', Income.date) == current_year).group_by('month').all()
    
    for m, val in incomes:
        if 1 <= m <= 12:
            monthly_income[int(m) - 1] = float(val or 0.0)
            
    expenses = db.session.query(
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount)
    ).filter(Expense.user_id == user_id, extract('year', Expense.date) == current_year).group_by('month').all()
    
    for m, val in expenses:
        if 1 <= m <= 12:
            monthly_expense[int(m) - 1] = float(val or 0.0)
            
    # 2. Expense Breakdown (Doughnut Chart): Sum of category expenses
    expense_categories = db.session.query(
        Expense.category,
        func.sum(Expense.amount)
    ).filter(Expense.user_id == user_id).group_by(Expense.category).all()
    
    breakdown_labels = [c[0] for c in expense_categories]
    breakdown_values = [float(c[1] or 0.0) for c in expense_categories]
    
    # 3. Budget Utilization: Category-wise limit vs actual spent
    budgets = Budget.query.filter(Budget.user_id == user_id, Budget.month == curr_month_str).all()
    budget_labels = []
    budget_limits = []
    budget_spent = []
    
    for b in budgets:
        budget_labels.append(b.category)
        budget_limits.append(b.limit_amount)
        spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.category == b.category,
            Expense.user_id == user_id,
            extract('year', Expense.date) == today.year,
            extract('month', Expense.date) == today.month
        ).scalar() or 0.0
        budget_spent.append(float(spent))
        
    # 4. Savings Progress
    savings_goals = SavingsGoal.query.filter_by(user_id=user_id).all()
    savings_labels = [sg.name for sg in savings_goals]
    savings_current = [sg.current_amount for sg in savings_goals]
    savings_target = [sg.target_amount for sg in savings_goals]

    return jsonify({
        'cashflow': {
            'labels': months_labels,
            'income': monthly_income,
            'expense': monthly_expense
        },
        'breakdown': {
            'labels': breakdown_labels,
            'values': breakdown_values
        },
        'budget': {
            'labels': budget_labels,
            'limits': budget_limits,
            'spent': budget_spent
        },
        'savings': {
            'labels': savings_labels,
            'current': savings_current,
            'target': savings_target
        }
    })

@dashboard_bp.route('/transactions')
def list_transactions():
    settings = get_current_settings()
    user_id = session['user_id']
    
    # Pagination & filtering parameters
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    tx_type = request.args.get('type', '')
    category_filter = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_by = request.args.get('sort', 'date_desc')
    
    incomes = Income.query.filter_by(user_id=user_id).all()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    
    tx_list = []
    for inc in incomes:
        tx_list.append({
            'id': inc.id,
            'type': 'Income',
            'date': inc.date,
            'category_or_source': inc.source,
            'amount': inc.amount,
            'description': inc.description or ''
        })
    for exp in expenses:
        tx_list.append({
            'id': exp.id,
            'type': 'Expense',
            'date': exp.date,
            'category_or_source': exp.category,
            'amount': exp.amount,
            'description': exp.description or ''
        })
        
    # Filter list
    if tx_type:
        tx_list = [tx for tx in tx_list if tx['type'] == tx_type]
    if category_filter:
        tx_list = [tx for tx in tx_list if tx['category_or_source'] == category_filter]
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            tx_list = [tx for tx in tx_list if tx['date'] >= start_dt]
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            tx_list = [tx for tx in tx_list if tx['date'] <= end_dt]
        except ValueError:
            pass
            
    # Sort list
    if sort_by == 'date_asc':
        tx_list.sort(key=lambda x: x['date'])
    elif sort_by == 'date_desc':
        tx_list.sort(key=lambda x: x['date'], reverse=True)
    elif sort_by == 'amount_asc':
        tx_list.sort(key=lambda x: x['amount'])
    elif sort_by == 'amount_desc':
        tx_list.sort(key=lambda x: x['amount'], reverse=True)
        
    total = len(tx_list)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_txs = tx_list[start:end]
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    categories = [
        "Part-Time Income", "Freelancing", "Scholarship", "Pocket Money", "Internship Stipend", "Business Income", "Other Income",
        "Food", "Transport", "Rent", "Education", "Books", "Shopping", "Entertainment", "Health", "Travel", "Subscriptions", "Other"
    ]
    
    return render_template(
        'transactions.html',
        settings=settings,
        transactions=paginated_txs,
        page=page,
        total_pages=total_pages,
        total=total,
        per_page=per_page,
        selected_type=tx_type,
        selected_category=category_filter,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        categories=categories
    )

@dashboard_bp.route('/settings', methods=['GET', 'POST'])
def view_settings():
    settings = get_current_settings()
    user_id = session['user_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'preferences':
            currency = request.form.get('currency', 'USD')
            theme = request.form.get('theme', 'light')
            export_pref = request.form.get('export_preference', 'excel')
            
            if currency != settings.currency and currency != 'USD' and not settings.is_premium:
                flash("Changing currency is a PRO feature. Please upgrade to Pro first!", "danger")
                return redirect(url_for('dashboard.view_settings'))
                
            settings.currency = currency
            settings.theme = theme
            settings.export_preference = export_pref
            db.session.commit()
            
            flash("Preferences updated successfully!", "success")
            
            # Smart redirect: if toggled via header form elsewhere, go back. Otherwise reload settings.
            referrer = request.referrer
            if referrer and 'settings' not in referrer and 'preferences' not in referrer:
                return redirect(referrer)
            return redirect(url_for('dashboard.view_settings'))
            
        elif action == 'backup':
            # Export user specific data as JSON (Multi-user safe, no SQLite locking issues)
            data = {
                'settings': settings.to_dict(),
                'incomes': [inc.to_dict() for inc in Income.query.filter_by(user_id=user_id).all()],
                'expenses': [exp.to_dict() for exp in Expense.query.filter_by(user_id=user_id).all()],
                'budgets': [b.to_dict() for b in Budget.query.filter_by(user_id=user_id).all()],
                'savings_goals': [sg.to_dict() for sg in SavingsGoal.query.filter_by(user_id=user_id).all()]
            }
            
            json_str = json.dumps(data, indent=2)
            json_io = io.BytesIO(json_str.encode('utf-8'))
            return send_file(
                json_io,
                as_attachment=True,
                download_name="finflow_backup.json",
                mimetype="application/json"
            )
            
        elif action == 'restore':
            file = request.files.get('backup_file')
            if not file or file.filename == '':
                flash("No file selected for restore.", "danger")
                return redirect(url_for('dashboard.view_settings'))
                
            try:
                # Read and parse JSON content
                backup_data = json.loads(file.read().decode('utf-8'))
                
                # Validation check
                required_keys = ['incomes', 'expenses', 'budgets', 'savings_goals']
                if not all(k in backup_data for k in required_keys):
                    flash("Invalid backup file format. Must be a valid FinFlow JSON backup.", "danger")
                    return redirect(url_for('dashboard.view_settings'))
                
                # Delete existing user records
                Income.query.filter_by(user_id=user_id).delete()
                Expense.query.filter_by(user_id=user_id).delete()
                Budget.query.filter_by(user_id=user_id).delete()
                SavingsGoal.query.filter_by(user_id=user_id).delete()
                
                # Restore incomes
                for item in backup_data.get('incomes', []):
                    date_val = datetime.strptime(item['date'], '%Y-%m-%d').date() if item.get('date') else date.today()
                    new_inc = Income(
                        user_id=user_id,
                        date=date_val,
                        source=item['source'],
                        amount=item['amount'],
                        description=item.get('description', '')
                    )
                    db.session.add(new_inc)
                    
                # Restore expenses
                for item in backup_data.get('expenses', []):
                    date_val = datetime.strptime(item['date'], '%Y-%m-%d').date() if item.get('date') else date.today()
                    new_exp = Expense(
                        user_id=user_id,
                        date=date_val,
                        category=item['category'],
                        amount=item['amount'],
                        description=item.get('description', '')
                    )
                    db.session.add(new_exp)
                    
                # Restore budgets
                for item in backup_data.get('budgets', []):
                    new_b = Budget(
                        user_id=user_id,
                        category=item['category'],
                        limit_amount=item['limit_amount'],
                        month=item['month']
                    )
                    db.session.add(new_b)
                    
                # Restore savings goals
                for item in backup_data.get('savings_goals', []):
                    date_val = datetime.strptime(item['target_date'], '%Y-%m-%d').date() if item.get('target_date') else None
                    new_sg = SavingsGoal(
                        user_id=user_id,
                        name=item['name'],
                        target_amount=item['target_amount'],
                        current_amount=item['current_amount'],
                        target_date=date_val
                    )
                    db.session.add(new_sg)
                    
                # Restore settings
                if 'settings' in backup_data and backup_data['settings']:
                    settings.currency = backup_data['settings'].get('currency', 'USD')
                    settings.theme = backup_data['settings'].get('theme', 'light')
                    settings.export_preference = backup_data['settings'].get('export_preference', 'excel')
                
                db.session.commit()
                flash("Database records restored successfully from backup!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error restoring backup: {str(e)}", "danger")
                
            return redirect(url_for('dashboard.home'))

    return render_template('settings.html', settings=settings)

@dashboard_bp.route('/upgrade-pro', methods=['POST'])
def upgrade_pro():
    settings = get_current_settings()
    settings.is_premium = not settings.is_premium
    db.session.commit()
    if settings.is_premium:
        flash("Congratulations! You are now a PRO member! Thank you for supporting FinFlow.", "success")
    else:
        flash("Your account has been reverted to the Standard plan.", "warning")
    return redirect(request.referrer or url_for('dashboard.home'))
