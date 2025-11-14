import re

sample_raw_content = """
本月支出分类报告
还款 1.28万
休闲娱乐 8,030.47
餐饮 5,230.89
交通 2,150.50
购物 3,850.00
水电费 980.23
总计 32,041.09
"""

# 测试正则表达式
pattern = r"(.+?)\s*((?:\d+,\d+|\d+)\.\d+(?:万)?|(?:\d+\.\d+|\d+)\s*万)"
matches = re.findall(pattern, sample_raw_content, re.DOTALL)

print("正则匹配结果：")
for match in matches:
    print(f"匹配组1：'{match[0]}'")
    print(f"匹配组2：'{match[1]}'")
    print()
