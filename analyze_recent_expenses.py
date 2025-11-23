from app import db
from app.models import Expense
from collections import defaultdict

def analyze_recent_expenses():
    # 分析2024年和2025年的支出
    years = [2024, 2025]
    yearly_expenses = {}
    yearly_category_expenses = {}
    
    for year in years:
        # 计算该年的总支出
        total_expense = 0
        category_expenses = defaultdict(float)
        
        for expense in Expense.query.all():
            if expense.date.year == year:
                total_expense += expense.amount
                category_expenses[expense.category] += expense.amount
        
        yearly_expenses[year] = total_expense
        yearly_category_expenses[year] = dict(category_expenses)
        
        print(f"\n{year}年总支出: {total_expense:.2f}元")
        print(f"{year}年支出分类:")
        # 按支出金额降序排序
        sorted_categories = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
        for category, amount in sorted_categories:
            print(f"  {category}: {amount:.2f}元")
    
    return yearly_expenses, yearly_category_expenses

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        analyze_recent_expenses()
