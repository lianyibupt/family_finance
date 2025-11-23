def compare_expenses():
    # 从之前的计算中获取数据
    average_annual_expense = 675055.70  # 11年平均支出
    expenses_2024 = 1089052.96  # 2024年总支出
    expenses_2025 = 3803421.67  # 2025年总支出
    
    # 计算差异
    diff_2024 = expenses_2024 - average_annual_expense
    diff_percent_2024 = (diff_2024 / average_annual_expense) * 100
    
    diff_2025 = expenses_2025 - average_annual_expense
    diff_percent_2025 = (diff_2025 / average_annual_expense) * 100
    
    # 生成对比报告
    print("=== 支出对比分析报告 ===")
    print(f"\n11年平均支出 (2014-2025): {average_annual_expense:,.2f}元")
    print(f"2024年总支出: {expenses_2024:,.2f}元")
    print(f"2024年与平均支出差异: {diff_2024:,.2f}元 ({diff_percent_2024:.2f}%)")
    print(f"2025年总支出: {expenses_2025:,.2f}元")
    print(f"2025年与平均支出差异: {diff_2025:,.2f}元 ({diff_percent_2025:.2f}%)")
    
    # 分析主要原因
    print("\n=== 主要差异原因分析 ===")
    print("1. 2025年支出显著高于平均水平，主要原因是:")
    print("   - 房租房贷支出达到2,293,900元，远高于2024年的230,700元")
    print("   - 转账给他人和还款支出也有较大增加")
    print("\n2. 2024年支出高于平均水平，主要原因是:")
    print("   - 转账给他人、房租房贷和还款是主要支出项")
    print("   - 亲子、购物和出行支出也占有一定比例")
    
    # 趋势分析
    print("\n=== 支出趋势分析 ===")
    print("1. 支出呈现明显上升趋势，从平均每年约67.5万元增长到2025年的380.3万元")
    print("2. 房产相关支出(房租房贷)是支出增长的主要驱动因素")
    print("3. 2025年可能有大额房产购买或投资行为")
    
    return {
        'average_expense': average_annual_expense,
        'expense_2024': expenses_2024,
        'expense_2025': expenses_2025,
        'diff_2024': diff_2024,
        'diff_percent_2024': diff_percent_2024,
        'diff_2025': diff_2025,
        'diff_percent_2025': diff_percent_2025
    }

if __name__ == '__main__':
    compare_expenses()
