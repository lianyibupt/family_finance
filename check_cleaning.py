#!/usr/bin/env python3
"""检查数据清理功能"""

from app.utils.ocr import LocalDeepSeekOCR

# 初始化OCR客户端
ocr_client = LocalDeepSeekOCR()

# 测试原始OCR文本（包含各种格式问题）
raw_content = '''
    还款    1.28万  
    
    休闲娱乐  
    8,030.47
    
    餐饮
    5,230.89交通 2,150.50
    
    购物  3,850.00
    
    水电费 980.23
    
    总计 32,041.09
'''

print('='*60)
print('原始OCR文本：')
print('='*60)
print(raw_content)
print()

# 测试数据清理功能
cleaned_content = ocr_client.clean_raw_content(raw_content)
print('='*60)
print('清理后的文本：')
print('='*60)
print(cleaned_content)
print()

# 测试行合并功能
merged_content = ocr_client.merge_lines(cleaned_content)
print('='*60)
print('合并后的文本：')
print('='*60)
print(merged_content)
print()

# 测试解析功能
parsed_result = ocr_client.parse_category_report(merged_content, report_type='expense')
print('='*60)
print('最终解析结果：')
print('='*60)
print(f'总金额：¥{parsed_result["total_amount"]}')
print(f'分类数量：{parsed_result["category_count"]}')
print()

for category in parsed_result["categories"]:
    print(f'  {category["category_name"]}: ¥{category["amount"]}')

print('\n' + '='*60)
print('数据清理功能检查完成！')
print('='*60)
