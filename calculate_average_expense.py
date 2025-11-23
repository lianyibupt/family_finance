def calculate_average_expense():
    # 从之前的计算中获取数据
    total_income = 14803612.66  # 从2014年开始的总收入
    net_worth = 7378000.00  # 当前家庭净资产
    years = 11  # 2014年到2025年共11年
    
    # 计算11年的总支出
    total_expense = total_income - net_worth
    
    # 计算平均每年支出
    average_annual_expense = total_expense / years
    
    print(f"11年总支出: {total_expense:.2f}元")
    print(f"平均每年支出: {average_annual_expense:.2f}元")
    
    return total_expense, average_annual_expense

if __name__ == '__main__':
    calculate_average_expense()
