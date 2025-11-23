from app import db
from app.models import Income
from datetime import datetime

def calculate_total_income():
    # 获取从2014年开始的所有收入记录
    total_income = 0
    for income in Income.query.all():
        if income.date.year >= 2014:
            # 考虑period_type，对于annual类型的数据，可能需要特殊处理
            # 但根据需求，我们只需要简单累加所有金额
            total_income += income.amount
    
    print(f"从2014年开始的总收入: {total_income:.2f}")
    return total_income

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        calculate_total_income()
