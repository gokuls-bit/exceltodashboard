from flask import Blueprint, render_template, request
from database.models import db, Income, Expense, Budget, SavingsGoal, Settings
from datetime import datetime, date
from sqlalchemy import extract, func, or_

reports_bp = Blueprint('reports', __name__)

def get_current_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(currency='USD', theme='light', export_preference='excel')
        db.session.add(settings)
        db.session.commit()
    return settings

@reports_bp.route('/reports', methods=['GET'])
def view_reports():
    settings = get_current_settings()
    
    # Report Parameters
    report_type = request.args.get('type', 'monthly')  # monthly, quarterly, yearly, custom
    selected_month = request.args.get('month', date.today().strftime('%Y-%m'))
    selected_quarter = request.args.get('quarter', f"{date.today().year}-Q{((date.today().month-1)//3)+1}")  # e.g. 2026-Q2
    selected_year = request.args.get('year', str(date.today().year))
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Calculate date range depending on report type
    start_dt = None
    end_dt = None
    
    if report_type == 'monthly':
        try:
            year, month = map(int, selected_month.split('-'))
            start_dt = date(year, month, 1)
            if month == 12:
                end_dt = date(year + 1, 1, 1)
            else:
                end_dt = date(year, month + 1, 1)
        except ValueError:
            pass
    elif report_type == 'quarterly':
        try:
            year_str, q_str = selected_quarter.split('-Q')
            year = int(year_str)
            q = int(q_str)
            if q == 1:
                start_dt = date(year, 1, 1)
                end_dt = date(year, 4, 1)
            elif q == 2:
                start_dt = date(year, 4, 1)
                end_dt = date(year, 7, 1)
            elif q == 3:
                start_dt = date(year, 7, 1)
                end_dt = date(year, 10, 1)
            elif q == 4:
                start_dt = date(year, 10, 1)
                end_dt = date(year + 1, 1, 1)
        except ValueError:
            pass
    elif report_type == 'yearly':
        try:
            year = int(selected_year)
            start_dt = date(year, 1, 1)
            end_dt = date(year + 1, 1, 1)
        except ValueError:
            pass
    elif report_type == 'custom':
        try:
            if start_date_str:
                start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if end_date_str:
                # Add 1 day to make the filter inclusive
                end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Fetch data
    income_query = Income.query
    expense_query = Expense.query
    
    if start_dt:
        income_query = income_query.filter(Income.date >= start_dt)
        expense_query = expense_query.filter(Expense.date >= start_dt)
    if end_dt:
        if report_type in ['monthly', 'quarterly', 'yearly']:
            # end_dt is the start of the next period (exclusive)
            income_query = income_query.filter(Income.date < end_dt)
            expense_query = expense_query.filter(Expense.date < end_dt)
        else:
            # custom end date is inclusive
            income_query = income_query.filter(Income.date <= end_dt)
            expense_query = expense_query.filter(Expense.date <= end_dt)
            
    incomes = income_query.order_by(Income.date.asc()).all()
    expenses = expense_query.order_by(Expense.date.asc()).all()
    
    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    net_savings = total_income - total_expense
    
    # Source Summary
    source_summary = {}
    for i in incomes:
        source_summary[i.source] = source_summary.get(i.source, 0.0) + i.amount
        
    # Category Summary
    category_summary = {}
    for e in expenses:
        category_summary[e.category] = category_summary.get(e.category, 0.0) + e.amount
        
    # Budget Summary (for monthly/quarterly/yearly, check limits)
    # If monthly, fetch that month's budget
    budget_limit = 0.0
    if report_type == 'monthly':
        budget_limit = db.session.query(func.sum(Budget.limit_amount)).filter(Budget.month == selected_month).scalar() or 0.0
    elif report_type == 'quarterly':
        # Sum budgets for the three months of the quarter
        year_str, q_str = selected_quarter.split('-Q')
        q = int(q_str)
        months = [f"{year_str}-0{q*3-2}", f"{year_str}-0{q*3-1}", f"{year_str}-0{q*3}"] if q*3-2 < 10 else [f"{year_str}-{q*3-2}", f"{year_str}-{q*3-1}", f"{year_str}-{q*3}"]
        budget_limit = db.session.query(func.sum(Budget.limit_amount)).filter(Budget.month.in_(months)).scalar() or 0.0
    elif report_type == 'yearly':
        # Sum budgets for all 12 months
        budget_limit = db.session.query(func.sum(Budget.limit_amount)).filter(Budget.month.like(f"{selected_year}-%")).scalar() or 0.0
        
    budget_adherence_status = "N/A"
    if budget_limit > 0:
        if total_expense > budget_limit:
            budget_adherence_status = f"Overspent by {settings.currency} {round(total_expense - budget_limit, 2)}"
        else:
            budget_adherence_status = f"Under budget by {settings.currency} {round(budget_limit - total_expense, 2)}"
            
    # Chart Data formatting
    # Category Breakdown
    chart_category_labels = list(category_summary.keys())
    chart_category_values = list(category_summary.values())
    
    # Source Breakdown
    chart_source_labels = list(source_summary.keys())
    chart_source_values = list(source_summary.values())
    
    return render_template(
        'reports.html',
        settings=settings,
        report_type=report_type,
        selected_month=selected_month,
        selected_quarter=selected_quarter,
        selected_year=selected_year,
        start_date=start_date_str,
        end_date=end_date_str,
        incomes=incomes,
        expenses=expenses,
        total_income=total_income,
        total_expense=total_expense,
        net_savings=net_savings,
        source_summary=source_summary,
        category_summary=category_summary,
        budget_limit=budget_limit,
        budget_adherence_status=budget_adherence_status,
        chart_category_labels=chart_category_labels,
        chart_category_values=chart_category_values,
        chart_source_labels=chart_source_labels,
        chart_source_values=chart_source_values
    )
