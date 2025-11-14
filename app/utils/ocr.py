import requests
import base64
import json
import os
import re

class LocalDeepSeekOCR:
    def __init__(self, api_url="http://localhost:1234/v1/chat/completions"):
        """
        初始化本地LMstudio客户端
        :param api_url: LMstudio OCR服务地址
        """
        self.api_url = api_url
        self.default_headers = {
            "Content-Type": "application/json"
        }
    
    def image_to_base64(self, image_path):
        """
        将图像文件转换为base64编码
        :param image_path: 图像文件路径
        :return: base64编码字符串
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def clean_raw_content(self, raw_content):
        """
        数据清理：移除格式符、处理换行等，保留合理的结构
        :param raw_content: 原始提取的文本
        :return: 清理后的文本
        """
        import re
        
        # 移除制表符和其他格式符
        content = raw_content.replace('\t', ' ')
        content = content.replace('\r', '')
        
        # 处理每行内容：移除行首行尾空格，保留换行符
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # 只保留非空行
                # 移除行内连续空格
                line = re.sub(r'\s+', ' ', line)
                cleaned_lines.append(line)
        
        # 将清理后的行重新组合，保留换行结构
        return '\n'.join(cleaned_lines)
    
    def clean_special_chars(self, text):
        """
        清理特殊符号，只保留中文、英文和必要的空格
        :param text: 原始文本
        :return: 清理后的文本
        """
        import re
        
        # 只保留中文、英文
        # 匹配中文：[\u4e00-\u9fa5]
        # 匹配英文：[a-zA-Z]
        # 匹配空格：\s
        cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', '', text)
        
        # 移除多余的空格
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text

    def merge_lines(self, cleaned_content):
        """
        行合并处理：将分类名称和金额合并到同一行
        :param cleaned_content: 清理后的文本
        :return: 合并后的文本
        """
        import re
        
        lines = cleaned_content.split('\n')
        merged_lines = []
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否为金额行
            amount_pattern = r'^\d+,\d+\.\d+|\d+\.\d+万?$'
            if re.match(amount_pattern, line):
                if current_category:
                    # 将金额与前一个分类合并
                    merged_lines.append(f"{current_category} {line}")
                    current_category = None
                else:
                    # 单独的金额行，可能是格式问题，直接保留
                    merged_lines.append(line)
            else:
                # 检查是否包含金额（支持货币符号 ¥、$，可选 ** 包裹）
                has_amount = re.search(r'((?:\*\*)?[¥$]?\s*(?:\d+,\d+|\d+)\.\d+(?:万)?|(?:\*\*)?[¥$]?\s*(?:\d+\.\d+|\d+)\s*万)(?:\*\*)?$', line)
                if has_amount:
                    # 已经包含金额的行，直接保留
                    merged_lines.append(line)
                else:
                    # 可能是分类名称行或块格式行
                    # 检查是否为块格式行（包含多个 -）
                    if '-' in line and line.count('-') >= 2:
                        # 块格式行，直接保留
                        merged_lines.append(line)
                    else:
                        # 分类名称行
                        current_category = line
        
        return '\n'.join(merged_lines)

    def extract_raw_content(self, image_path, model_name="qwen/qwen3-vl-4b", temperature=0.1):
        """
        提取图像中的原始文本内容
        :param image_path: 图像路径
        :param model_name: 模型名称
        :param temperature: 生成温度，设置为低确保输出稳定
        :return: 原始提取的文本内容
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # 转换图像为base64
        base64_image = self.image_to_base64(image_path)
        
        # 构建请求 payload
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的OCR识别专家：
1. 请从人的视角来进行理解提取，仅提取与交易相关的内容
2. 最终输出只保留：交易类型、金额。以纯文本形式输出，每行一个项目，每个项目包含交易类型和金额。
3. 严禁以任何形式输出表格或HTML标签。严禁使用任何表格结构、HTML标签或Markdown表格语法。"
"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请提取银行分类报告中的交易类别和金额"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": temperature,
            "max_tokens": -1,
            "stream": False
        }
        
        try:
            # 发送请求
            response = requests.post(
                url=self.api_url,
                headers=self.default_headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OCR API调用失败: {str(e)}") from e
        except Exception as e:
            raise Exception(f"文本提取失败: {str(e)}") from e

    def parse_category_report(self, raw_content, report_type="expense"):
        """
        解析银行分类报告（收入/支出分类）
        :param raw_content: OCR提取的原始文本
        :param report_type: 报告类型："income"或"expense"
        :return: 结构化的分类数据
        """
        import re
        
        # 定义金额和分类的正则表达式模式
        # 匹配 "分类名称 金额" 格式，支持数字格式：1.28万、8030.47、8,030.47，支持货币符号 ¥、$
        pattern = r"(.+?)\s*([¥$]?\s*((?:\d+,\d+|\d+)\.\d+(?:万)?|(?:\d+\.\d+|\d+)\s*万))"
        
        categories = []
        
        # 处理内容：支持分块和单行格式
        content_blocks = raw_content.split("\n\n")  # 按段落分块
        
        for block in content_blocks:
            block = block.strip()
            if not block:
                continue
                
            # 逐行处理块内内容
            lines = block.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 尝试块格式处理
                block_processed = False
                
                # 1. 先按 #### 分割成不同的区块（如果有）
                sections = line.split("####")
                
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue
                        
                    # 2. 在每个区块内，按 "-" 分割为多个分类-金额对
                    tokens = [t.strip() for t in section.split("-") if t.strip()]
                    
                    if len(tokens) >= 2:
                        # 检查是否为有效的分类-金额对列表
                        for i in range(0, len(tokens) - 1, 2):
                            category_name_candidate = tokens[i]
                            amount_str_candidate = tokens[i + 1]
                            
                            # 验证金额格式（支持可选的 ** 包裹）
                            amount_pattern = r'^\s*(?:\*\*)?[¥$]?\s*((?:\d+,\d+|\d+)\.\d+(?:万)?|(?:\d+\.\d+|\d+)\s*万)\s*(?:\*\*)?$'
                            if re.match(amount_pattern, amount_str_candidate):
                                # 清理分类名称
                                category_name = self.clean_special_chars(category_name_candidate)
                                
                                # 跳过汇总行
                                if category_name in ["总计", "总额", "合计"]:
                                    continue
                                    
                                # 转换金额为数字格式
                                try:
                                    amount_str = amount_str_candidate.replace(",", "")  # 移除千位分隔符
                                    amount_str = amount_str.replace("**", "")  # 移除 ** 包裹
                                    amount_str = re.sub(r'[¥$]', '', amount_str)  # 移除货币符号
                                    
                                    if "万" in amount_str:
                                        num_part = amount_str.replace("万", "").strip()
                                        amount = float(num_part) * 10000
                                    else:
                                        amount = float(amount_str)
                                        
                                    categories.append({
                                        "category_name": category_name,
                                        "amount": amount,
                                        "type": "income" if report_type == "income" else "expense"
                                    })
                                    
                                    block_processed = True  # 标记为已处理块格式
                                    
                                except ValueError as e:
                                    print(f"警告：无法转换金额 {amount_str_candidate} 为数字，跳过该记录")
                                    continue
                
                # 如果块格式处理没有成功匹配，尝试原始行匹配
                if not block_processed:
                    match = re.match(pattern, line)
                    if not match:
                        continue
                        
                    # 清理分类名称和金额
                    category_name = match.group(1).strip()
                    amount_str = match.group(2).strip()
                    
                    # 清理特殊符号，只保留中文和英文
                    category_name = self.clean_special_chars(category_name)
                    
                    # 跳过汇总行
                    if category_name in ["总计", "总额", "合计"]:
                        continue
                        
                    # 转换金额为数字格式
                    try:
                        amount_str = amount_str.replace(",", "")  # 移除千位分隔符
                        amount_str = re.sub(r'[¥$]', '', amount_str)  # 移除货币符号
                        
                        if "万" in amount_str:
                            num_part = amount_str.replace("万", "").strip()
                            amount = float(num_part) * 10000
                        else:
                            amount = float(amount_str)
                            
                        categories.append({
                            "category_name": category_name,
                            "amount": amount,
                            "type": "income" if report_type == "income" else "expense"
                        })
                        
                    except ValueError as e:
                        print(f"警告：无法转换金额 {amount_str} 为数字，跳过该记录")
                        continue  # 跳过无法转换的金额
        
        # 计算总计
        total_amount = sum(cat["amount"] for cat in categories)
        
        return {
            "report_type": report_type,
            "total_amount": total_amount,
            "category_count": len(categories),
            "categories": categories
        }

    def analyze_bank_report(self, image_path, report_type="expense", model_name="qwen/qwen3-vl-4b"):
        """
        分析银行分类报告图像（收入/支出分类）
        :param image_path: 报告图像路径
        :param report_type: 报告类型："income"或"expense"
        :param model_name: 模型名称
        :return: 结构化分析结果
        """
        # 先提取原始文本
        raw_content = self.extract_raw_content(image_path, model_name=model_name)
        
        # 检查是否包含HTML表格
        if '<table>' in raw_content:
            # 直接解析HTML表格
            structured_data = self.parse_html_table(raw_content, report_type=report_type)
            if structured_data:
                return {
                    "raw_content": raw_content,  # 保留原始提取内容
                    "cleaned_content": raw_content,  # HTML内容无需清理
                    "merged_content": raw_content,  # HTML内容无需合并
                    "structured_data": structured_data  # 结构化分析结果
                }
        
        # 数据清理：移除格式符和多余换行
        cleaned_content = self.clean_raw_content(raw_content)
        
        # 行合并处理：将分类名称和金额合并到同一行
        merged_content = self.merge_lines(cleaned_content)
        
        # 然后解析为分类数据
        structured_data = self.parse_category_report(merged_content, report_type=report_type)
        
        return {
            "raw_content": raw_content,  # 保留原始提取内容
            "cleaned_content": cleaned_content,  # 保留清理后的内容
            "merged_content": merged_content,  # 保留合并后的内容
            "structured_data": structured_data  # 结构化分析结果
        }

    
    def extract_valid_category_amounts(self, ocr_result):
        """
        从OCR结果中提取有效类别和金额数据（标准化接口）
        :param ocr_result: 来自analyze_bank_report的完整结果
        :return: 标准化的类别-金额数据列表
        """
        structured_data = ocr_result['structured_data']
        
        # 确保categories字段存在
        if 'categories' not in structured_data:
            return []
        
        # 提取有效类别和金额
        valid_data = []
        for category in structured_data['categories']:
            if 'category_name' in category and 'amount' in category:
                valid_data.append({
                    'name': category['category_name'],
                    'amount': category['amount'],
                    'type': category['type']
                })
        
        return valid_data
    
    def analyze_general_image(self, image_path, prompt, model_name="qwen/qwen3-vl-4b", temperature=0.7):
        """
        通用图像分析
        :param image_path: 图像路径
        :param prompt: 用户提示
        :param model_name: 模型名称
        :param temperature: 生成温度
        :return: OCR结果
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        base64_image = self.image_to_base64(image_path)
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的图像识别专家。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "temperature": temperature,
            "max_tokens": 1000,
            "stream": False
        }
        
        response = requests.post(self.api_url, headers=self.default_headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _convert_amount(self, amount_str):
        """将金额字符串转换为数字"""
        if not amount_str:
            return None
            
        # 移除多余字符
        amount_str = amount_str.replace('*', '')
        amount_str = amount_str.replace(' ', '')
        
        # 处理万元单位
        if '万' in amount_str:
            num_part = amount_str.replace('万', '')
            # 移除货币符号
            num_part = num_part.replace('¥', '')
            try:
                return float(num_part) * 10000
            except ValueError:
                return None
        
        # 处理普通金额格式
        num_part = amount_str.replace('¥', '')
        num_part = num_part.replace(',', '')
        try:
            return float(num_part)
        except ValueError:
            return None
    
    def parse_html_table(self, html_content, report_type="expense"):
        """
        解析HTML表格并提取“对比去年”之后的有效交易数据
        :param html_content: HTML表格内容
        :return: 结构化的交易数据
        """
        from bs4 import BeautifulSoup
        import pandas as pd
        
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        
        if not tables:
            return None
            
        table = tables[0]  # 处理第一个表格
        rows = table.find_all('tr')
        
        # 解析表头
        headers = []
        header_row = rows[0]
        header_cells = header_row.find_all('td')
        for cell in header_cells:
            headers.append(cell.get_text(strip=True))
        
        # 解析表格数据
        table_data = []
        for row in rows[1:]:
            cells = row.find_all('td')
            row_data = []
            for cell in cells:
                row_data.append(cell.get_text(strip=True))
            
            # 确保行数据与表头长度一致
            if len(row_data) < len(headers):
                row_data += [''] * (len(headers) - len(row_data))
            
            table_data.append(row_data)
        
        df = pd.DataFrame(table_data, columns=headers)
        
        # 检测表格格式
        first_col = headers[0]
        second_col = headers[1] if len(headers) > 1 else ''
        
        # 处理简单的两列格式（如：支出项目 - 金额）
        if len(headers) == 2 and ('金额' in second_col or '元' in second_col or '万' in second_col):
            # 直接处理为单年度支出数据
            valid_transactions = []
            
            # 检查金额单位是否为万元
            is_ten_thousand_unit = '万元' in second_col
            
            for index, row in df.iterrows():
                transaction_type = row.iloc[0]
                amount = row.iloc[1]
                
                # 仅跳过空行和无效行，保留"更多(XX类)"行
                if not transaction_type or not amount:
                    continue
                
                converted_amount = self._convert_amount(amount)
                if converted_amount:
                    # 如果单位是万元，乘以10000
                    if is_ten_thousand_unit:
                        converted_amount *= 10000
                    
                    valid_transactions.append({
                        'transaction_type': transaction_type,
                        'amounts': [{
                            # 假设为当前年度或统一处理
                            'year': '2024-2025',
                            'amount': converted_amount
                        }],
                        'category': transaction_type
                    })
            
            # 计算总计信息
            total_amount = sum(transaction['amounts'][0]['amount'] for transaction in valid_transactions)
            
            # 转换为与文本解析一致的格式
            standardized_categories = []
            for transaction in valid_transactions:
                standardized_categories.append({
                    "category_name": transaction['transaction_type'],
                    "amount": transaction['amounts'][0]['amount'],
                    "type": report_type
                })
            
            return {
                "report_type": report_type,
                "total_amount": total_amount,
                "category_count": len(standardized_categories),
                "categories": standardized_categories
            }
        
        # 原有逻辑：处理年度对比格式
        # 提取交易数据的核心逻辑
        compare_row = df[df.iloc[:, 0] == '对比上年'].index
        
        if not compare_row.empty:
            compare_idx = compare_row[0]
            transaction_df = df.loc[compare_idx + 1:].reset_index(drop=True)
        else:
            transaction_df = df
            
        # 筛选有效交易数据
        valid_transactions = []
        
        for index, row in transaction_df.iterrows():
            transaction_type = row.iloc[0]
            # 跳过空行和无效行
            if not transaction_type:
                continue
                
            # 保留"更多(XX类)"行作为有效数据
                
            # 检查是否是餐饮类的更多条目行（兼容不同表格列数）
            if transaction_type == '餐饮':
                # 检查最后一列是否为'更多(XX类)'（使用正则匹配）
                if re.match(r'更多\s*\(\d+类\)', str(row.iloc[-1])):
                    continue
                
            # 收集所有非空金额列
            amounts = []
            for year_idx in range(1, len(row)):
                amount = row.iloc[year_idx]
                if amount:
                    converted_amount = self._convert_amount(amount)
                    if converted_amount:
                        amounts.append({
                            'year': df.columns[year_idx],
                            'amount': converted_amount
                        })
            
            if amounts:
                valid_transactions.append({
                    'transaction_type': transaction_type,
                    'amounts': amounts,
                    'category': transaction_type  # 统一字段名
                })
        
        # 转换为标准化格式
        standardized_categories = []
        
        for transaction in valid_transactions:
            # 对于年度对比表，选择最新年份的金额
            latest_year = max(transaction['amounts'], key=lambda x: x['year'])
            
            standardized_categories.append({
                "category_name": transaction['transaction_type'],
                "amount": latest_year['amount'],
                "type": report_type
            })
        
        # 计算总计信息
        total_amount = sum(category['amount'] for category in standardized_categories)
        
        return {
            "report_type": report_type,
            "total_amount": total_amount,
            "category_count": len(standardized_categories),
            "categories": standardized_categories
        }
