from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app import db
from app.models import Income, Expense, Asset, Liability
import pandas as pd
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.ocr import LocalDeepSeekOCR
import matplotlib
matplotlib.use('Agg')  # 非GUI后端
import matplotlib.pyplot as plt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/import', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        # 检查是否有文件部分
        if 'file' not in request.files:
            flash('没有文件部分', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        data_type = request.form['data_type']
        
        # 检查文件名
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # 读取CSV文件
                df = pd.read_csv(file_path)
                
                # 根据数据类型处理
                if data_type == 'income':
                    import_income(df)
                elif data_type == 'expense':
                    import_expense(df)
                elif data_type == 'asset':
                    import_asset(df)
                elif data_type == 'liability':
                    import_liability(df)
                
                flash('数据导入成功！', 'success')
                
            except Exception as e:
                flash(f'导入失败：{str(e)}', 'error')
            finally:
                # 删除上传的文件
                os.remove(file_path)
                
            return redirect(url_for('main.import_data'))
    
    return render_template('import.html')

def import_income(df):
    """导入收入数据"""
    for _, row in df.iterrows():
        # 检查是否有period_type列，如果没有默认设置为'monthly'
        period_type = row.get('period_type', 'monthly').lower()
        # 确保period_type只能是'monthly'或'annual'
        period_type = 'monthly' if period_type not in ['monthly', 'annual'] else period_type
        
        income = Income(
            date=pd.to_datetime(row['date']).date(),
            category=row['category'],
            amount=float(row['amount']),
            source=row['source'],
            period_type=period_type,
            description=row['description'] if 'description' in row and pd.notna(row['description']) else None
        )
        db.session.add(income)
    db.session.commit()

def import_expense(df):
    """导入支出数据"""
    for _, row in df.iterrows():
        # 检查是否有period_type列，如果没有默认设置为'monthly'
        period_type = row.get('period_type', 'monthly').lower()
        # 确保period_type只能是'monthly'或'annual'
        period_type = 'monthly' if period_type not in ['monthly', 'annual'] else period_type
        
        expense = Expense(
            date=pd.to_datetime(row['date']).date(),
            category=row['category'],
            amount=float(row['amount']),
            payer=row['payer'],
            period_type=period_type,
            description=row['description'] if 'description' in row and pd.notna(row['description']) else None
        )
        db.session.add(expense)
    db.session.commit()

def import_asset(df):
    """导入资产数据"""
    for _, row in df.iterrows():
        # 检查是否有period_type列，如果没有默认设置为'monthly'
        period_type = row.get('period_type', 'monthly').lower()
        # 确保period_type只能是'monthly'或'annual'
        period_type = 'monthly' if period_type not in ['monthly', 'annual'] else period_type
        
        asset = Asset(
            name=row['name'],
            type=row['type'],
            amount=float(row['amount']),
            owner=row['owner'],
            update_date=pd.to_datetime(row['update_date']).date(),
            period_type=period_type,
            description=row['description'] if 'description' in row and pd.notna(row['description']) else None
        )
        db.session.add(asset)
    db.session.commit()

def import_liability(df):
    """导入负债数据"""
    for _, row in df.iterrows():
        # 检查是否有period_type列，如果没有默认设置为'monthly'
        period_type = row.get('period_type', 'monthly').lower()
        # 确保period_type只能是'monthly'或'annual'
        period_type = 'monthly' if period_type not in ['monthly', 'annual'] else period_type
        
        liability = Liability(
            name=row['name'],
            type=row['type'],
            amount=float(row['amount']),
            owner=row['owner'],
            update_date=pd.to_datetime(row['update_date']).date(),
            period_type=period_type,
            description=row['description'] if 'description' in row and pd.notna(row['description']) else None
        )
        db.session.add(liability)
    db.session.commit()

@main.route('/income_statement', methods=['GET'])
def income_statement():
    """收入利润表"""
    year = request.args.get('year', datetime.now().year)
    period_type = request.args.get('period_type', 'all')
    
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    # 查询收入和支出，并根据period_type过滤
    if period_type == 'all':
        incomes = Income.query.filter(db.extract('year', Income.date) == year).all()
        expenses = Expense.query.filter(db.extract('year', Expense.date) == year).all()
    else:
        incomes = Income.query.filter(
            db.extract('year', Income.date) == year,
            Income.period_type == period_type
        ).all()
        expenses = Expense.query.filter(
            db.extract('year', Expense.date) == year,
            Expense.period_type == period_type
        ).all()
    
    # 计算总收入和总支出
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    net_surplus = total_income - total_expense
    
    # 按类别汇总
    categories = set()
    category_data = {}
    
    # 处理收入
    for income in incomes:
        categories.add(income.category)
        if income.category not in category_data:
            category_data[income.category] = {'income': 0, 'expense': 0, 'surplus': 0}
        category_data[income.category]['income'] += income.amount
    
    # 处理支出
    for expense in expenses:
        categories.add(expense.category)
        if expense.category not in category_data:
            category_data[expense.category] = {'income': 0, 'expense': 0, 'surplus': 0}
        category_data[expense.category]['expense'] += expense.amount
    
    # 计算结余
    for category in categories:
        if category in category_data:
            category_data[category]['surplus'] = category_data[category]['income'] - category_data[category]['expense']
    
    # 生成收入支出对比柱状图
    categories_list = sorted(list(categories))
    income_values = [category_data[cat]['income'] for cat in categories_list]
    expense_values = [category_data[cat]['expense'] for cat in categories_list]
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = range(len(categories_list))
    
    ax.bar(index, income_values, bar_width, label='收入', color='#10B981')
    ax.bar([i + bar_width for i in index], expense_values, bar_width, label='支出', color='#EF4444')
    
    ax.set_xlabel('类别')
    ax.set_ylabel('金额(元)')
    ax.set_title(f'{year}年收入支出对比')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(categories_list, rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 保存图表到临时文件
    chart_filename = f'income_statement_chart_{year}.png'
    chart_path = os.path.join(current_app.static_folder, 'charts', chart_filename)
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return render_template('income_statement.html',
                           year=year,
                           total_income=total_income,
                           total_expense=total_expense,
                           net_surplus=net_surplus,
                           categories=categories_list,
                           category_data=category_data,
                           chart_filename=chart_filename)

@main.route('/balance_sheet', methods=['GET'])
def balance_sheet():
    """资产负债表"""
    year = request.args.get('year', datetime.now().year)
    period_type = request.args.get('period_type', 'all')
    
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    # 查询资产和负债，并根据period_type过滤
    if period_type == 'all':
        assets = Asset.query.filter(db.extract('year', Asset.update_date) == year).all()
        liabilities = Liability.query.filter(db.extract('year', Liability.update_date) == year).all()
    else:
        assets = Asset.query.filter(
            db.extract('year', Asset.update_date) == year,
            Asset.period_type == period_type
        ).all()
        liabilities = Liability.query.filter(
            db.extract('year', Liability.update_date) == year,
            Liability.period_type == period_type
        ).all()
    
    # 计算总资产和总负债
    total_assets = sum(asset.amount for asset in assets)
    total_liabilities = sum(liability.amount for liability in liabilities)
    net_worth = total_assets - total_liabilities
    
    # 生成资产负债对比柱状图
    # 按类型分组资产和负债
    asset_types = {}  # type: amount
    liability_types = {}  # type: amount
    
    for asset in assets:
        if asset.type not in asset_types:
            asset_types[asset.type] = 0
        asset_types[asset.type] += asset.amount
    
    for liability in liabilities:
        if liability.type not in liability_types:
            liability_types[liability.type] = 0
        liability_types[liability.type] += liability.amount
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 准备图表数据
    all_types = list(set(list(asset_types.keys()) + list(liability_types.keys())))
    all_types.sort()
    
    asset_values = [asset_types.get(atype, 0) for atype in all_types]
    liability_values = [liability_types.get(atype, 0) for atype in all_types]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = range(len(all_types))
    
    ax.bar(index, asset_values, bar_width, label='资产', color='#10B981')
    ax.bar([i + bar_width for i in index], liability_values, bar_width, label='负债', color='#EF4444')
    
    ax.set_xlabel('类别')
    ax.set_ylabel('金额(元)')
    ax.set_title(f'{year}年资产负债对比')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(all_types, rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 保存图表到临时文件
    chart_filename = f'balance_sheet_chart_{year}.png'
    chart_path = os.path.join(current_app.static_folder, 'charts', chart_filename)
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return render_template('balance_sheet.html',
                           year=year,
                           assets=assets,
                           liabilities=liabilities,
                           total_assets=total_assets,
                           total_liabilities=total_liabilities,
                           net_worth=net_worth,
                           chart_filename=chart_filename)

@main.route('/cash_flow', methods=['GET'])
def cash_flow():
    """现金流量表"""
    year = request.args.get('year', datetime.now().year)
    period_type = request.args.get('period_type', 'all')
    
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    # 查询收入和支出，并根据period_type过滤
    if period_type == 'all':
        incomes = Income.query.filter(db.extract('year', Income.date) == year).all()
        expenses = Expense.query.filter(db.extract('year', Expense.date) == year).all()
    else:
        incomes = Income.query.filter(
            db.extract('year', Income.date) == year,
            Income.period_type == period_type
        ).all()
        expenses = Expense.query.filter(
            db.extract('year', Expense.date) == year,
            Expense.period_type == period_type
        ).all()
    
    # 组织现金流量项目
    cash_flow_items = []
    
    for income in incomes:
        cash_flow_items.append({
            'date': income.date,
            'type': 'income',
            'category': income.category,
            'amount': income.amount
        })
    
    for expense in expenses:
        cash_flow_items.append({
            'date': expense.date,
            'type': 'expense',
            'category': expense.category,
            'amount': expense.amount
        })
    
    # 按日期排序
    cash_flow_items.sort(key=lambda x: x['date'])
    
    # 计算现金流量
    operating_inflow = sum(item['amount'] for item in cash_flow_items if item['type'] == 'income')
    operating_outflow = sum(item['amount'] for item in cash_flow_items if item['type'] == 'expense')
    net_operating_flow = operating_inflow - operating_outflow
    
    # 生成现金流量对比柱状图
    # 按类别分组现金流入和流出
    inflow_by_category = {}  # category: amount
    outflow_by_category = {}  # category: amount
    
    for item in cash_flow_items:
        if item['type'] == 'income':
            if item['category'] not in inflow_by_category:
                inflow_by_category[item['category']] = 0
            inflow_by_category[item['category']] += item['amount']
        else:
            if item['category'] not in outflow_by_category:
                outflow_by_category[item['category']] = 0
            outflow_by_category[item['category']] += item['amount']
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 准备图表数据
    all_categories = list(set(list(inflow_by_category.keys()) + list(outflow_by_category.keys())))
    all_categories.sort()
    
    inflow_values = [inflow_by_category.get(cat, 0) for cat in all_categories]
    outflow_values = [outflow_by_category.get(cat, 0) for cat in all_categories]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = range(len(all_categories))
    
    ax.bar(index, inflow_values, bar_width, label='现金流入', color='#10B981')
    ax.bar([i + bar_width for i in index], outflow_values, bar_width, label='现金流出', color='#EF4444')
    
    ax.set_xlabel('类别')
    ax.set_ylabel('金额(元)')
    ax.set_title(f'{year}年现金流量对比')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(all_categories, rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 保存图表到临时文件
    chart_filename = f'cash_flow_chart_{year}.png'
    chart_path = os.path.join(current_app.static_folder, 'charts', chart_filename)
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return render_template('cash_flow.html',
                           year=year,
                           cash_flow_items=cash_flow_items,
                           operating_inflow=operating_inflow,
                           operating_outflow=operating_outflow,
                           net_operating_flow=net_operating_flow,
                           chart_filename=chart_filename)

@main.route('/import/image', methods=['GET', 'POST'])
def import_image():
    """图像OCR导入功能"""
    # 生成当前年月默认值
    current_year_month = datetime.now().strftime('%Y-%m')
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('没有文件部分', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        report_month = request.form['report_month']
        data_type = request.form['data_type']
        owner = request.form['owner']
        
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        if file and (file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png')):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # 初始化OCR客户端
                ocr_client = LocalDeepSeekOCR(api_url="http://localhost:1234/v1/chat/completions")
                
                # 调用OCR分析银行分类报告
                ocr_result = ocr_client.analyze_bank_report(
                    image_path=file_path, 
                    report_type=data_type  # 传入收入/支出类型
                    # 使用默认模型 qwen/qwen3-vl-4b
                )
                
                # 跳转到OCR识别预览页面，让用户确认后再导入
                return render_template('ocr_preview.html',
                                    raw_content=ocr_result['raw_content'],
                                    merged_content=ocr_result['merged_content'],
                                    categories=ocr_result['structured_data']['categories'],
                                    report_month=report_month,
                                    data_type=data_type,
                                    owner=owner)
            except Exception as e:
                flash(f"OCR识别失败：{str(e)}", "error")
            finally:
                # 删除上传的文件
                os.remove(file_path)
                
            return redirect(url_for('main.import_image'))
    
    # GET请求，返回带有默认日期的表单
    return render_template('import_image.html', current_year_month=current_year_month)

@main.route('/confirm_ocr_import', methods=['POST'])
def confirm_ocr_import():
    """确认OCR识别结果并导入"""
    from app.models import Income, Expense
    
    # 获取表单参数
    merged_content = request.form['merged_content']
    report_month = request.form['report_month']
    data_type = request.form['data_type']
    owner = request.form['owner']
    selected_items = request.form.getlist('selected_items')
    
    # 重新解析OCR结果
    from app.utils.ocr import LocalDeepSeekOCR
    ocr_client = LocalDeepSeekOCR()
    
    try:
        # 检查是否为HTML内容
        if '<table>' in merged_content:
            # 直接解析HTML表格
            structured_data = ocr_client.parse_html_table(merged_content, report_type=data_type)
            if not structured_data:
                flash(f"HTML表格解析失败", "error")
                return redirect(url_for('main.import_image'))
        else:
            # 解析合并后的内容（普通文本）
            structured_data = ocr_client.parse_category_report(merged_content, report_type=data_type)
        
        # 只导入用户选择的项
        imported_count = 0
        for i, category in enumerate(structured_data['categories']):
            if str(i) in selected_items:
                report_date = pd.to_datetime(f"{report_month}-01").date()
                
                if data_type == "income":
                    income = Income(
                        date=report_date,
                        category=category["category_name"],
                        amount=float(category["amount"]),
                        source=owner,
                        period_type='monthly',
                        description=f"OCR识别：{report_month} {data_type}分类汇总"
                    )
                    db.session.add(income)
                elif data_type == "expense":
                    expense = Expense(
                        date=report_date,
                        category=category["category_name"],
                        amount=float(category["amount"]),
                        payer=owner,
                        period_type='monthly',
                        description=f"OCR识别：{report_month} {data_type}分类汇总"
                    )
                    db.session.add(expense)
                
                imported_count += 1
        
        # 提交到数据库
        db.session.commit()
        flash(f"成功导入 {imported_count} 个分类记录！", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"导入失败：{str(e)}", "error")
    
    return redirect(url_for('main.data_list', data_type=data_type))
    
    # GET请求，返回带有默认日期的表单
    return render_template('import_image.html', current_year_month=current_year_month)

@main.route('/data_list', methods=['GET'])
def data_list():
    """详细数据列表页面"""
    from app.models import Income, Expense, Asset, Liability
    
    # 获取数据类型
    data_type = request.args.get('data_type', 'all')
    
    # 根据数据类型查询数据
    if data_type == 'income':
        data_items = Income.query.all()
    elif data_type == 'expense':
        data_items = Expense.query.all()
    elif data_type == 'asset':
        data_items = Asset.query.all()
    elif data_type == 'liability':
        data_items = Liability.query.all()
    else:
        # 查询所有类型数据
        data_items = []
        data_items.extend(Income.query.all())
        data_items.extend(Expense.query.all())
        data_items.extend(Asset.query.all())
        data_items.extend(Liability.query.all())
    
    return render_template('data_list.html', data_items=data_items, data_type=data_type)

@main.route('/edit_data', methods=['POST'])
def edit_data():
    """编辑数据"""
    from app.models import Income, Expense, Asset, Liability
    
    data_type = request.form['data_type']
    id = request.form['id']
    date = request.form['date']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form.get('description', '')
    
    # 根据数据类型更新
    if data_type == 'income':
        item = Income.query.get(id)
        if item:
            item.date = pd.to_datetime(date).date()
            item.category = category
            item.amount = float(amount)
            item.source = request.form['source']
            item.description = description
    elif data_type == 'expense':
        item = Expense.query.get(id)
        if item:
            item.date = pd.to_datetime(date).date()
            item.category = category
            item.amount = float(amount)
            item.payer = request.form['payer']
            item.description = description
    elif data_type == 'asset':
        item = Asset.query.get(id)
        if item:
            item.update_date = pd.to_datetime(date).date()
            item.type = category
            item.amount = float(amount)
            item.owner = request.form['owner']
            item.description = description
    elif data_type == 'liability':
        item = Liability.query.get(id)
        if item:
            item.update_date = pd.to_datetime(date).date()
            item.type = category
            item.amount = float(amount)
            item.owner = request.form['owner']
            item.description = description
    
    try:
        db.session.commit()
        flash('数据更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'数据更新失败：{str(e)}', 'error')
    
    return redirect(url_for('main.data_list', data_type=data_type))

@main.route('/delete_data', methods=['POST'])
def delete_data():
    """删除数据"""
    from app.models import Income, Expense, Asset, Liability
    
    data_type = request.form['data_type']
    id = request.form['id']
    
    # 根据数据类型删除
    if data_type == 'income':
        item = Income.query.get(id)
    elif data_type == 'expense':
        item = Expense.query.get(id)
    elif data_type == 'asset':
        item = Asset.query.get(id)
    elif data_type == 'liability':
        item = Liability.query.get(id)
    
    if item:
        try:
            db.session.delete(item)
            db.session.commit()
            flash('数据删除成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'数据删除失败：{str(e)}', 'error')
    else:
        flash('数据不存在！', 'error')
    
    return redirect(url_for('main.data_list', data_type=data_type))

@main.route('/data_cleanup', methods=['GET', 'POST'])
def data_cleanup():
    """数据清理功能"""
    from app.models import Income, Expense, Asset, Liability
    
    # 统计当前数据
    stats = {
        'income_count': Income.query.count(),
        'expense_count': Expense.query.count(),
        'asset_count': Asset.query.count(),
        'liability_count': Liability.query.count(),
        'total_count': Income.query.count() + Expense.query.count() + Asset.query.count() + Liability.query.count()
    }
    
    if request.method == 'POST':
        cleanup_type = request.form['cleanup_type']
        
        try:
            if cleanup_type == 'ocr':
                # 清理OCR导入的数据
                month = request.form['month']
                if not month:
                    flash('请选择月份', 'error')
                    return redirect(url_for('main.data_cleanup'))
                
                # 删除指定月份的OCR记录
                count = 0
                
                # 清理收入记录
                income_count = Income.query.filter(
                    db.extract('year', Income.date) == month[:4],
                    db.extract('month', Income.date) == month[5:7],
                    Income.description.like('%OCR识别%')
                ).delete()
                count += income_count
                
                # 清理支出记录
                expense_count = Expense.query.filter(
                    db.extract('year', Expense.date) == month[:4],
                    db.extract('month', Expense.date) == month[5:7],
                    Expense.description.like('%OCR识别%')
                ).delete()
                count += expense_count
                
                db.session.commit()
                flash(f'成功清理 {count} 条OCR导入记录', 'success')
                
            elif cleanup_type == 'duplicate':
                # 清理重复数据（简单实现）
                record_type = request.form['record_type']
                flash(f'重复数据清理功能正在开发中...', 'info')
                
            elif cleanup_type == 'manual':
                # 手工清理数据
                record_type = request.form['record_type']
                month = request.form.get('month')
                category = request.form.get('category')
                
                count = 0
                
                if record_type == 'income':
                    query = Income.query
                elif record_type == 'expense':
                    query = Expense.query
                elif record_type == 'asset':
                    query = Asset.query
                elif record_type == 'liability':
                    query = Liability.query
                else:
                    flash('无效的记录类型', 'error')
                    return redirect(url_for('main.data_cleanup'))
                
                # 构建查询条件
                if month:
                    query = query.filter(
                        db.extract('year', Income.date) == month[:4],
                        db.extract('month', Income.date) == month[5:7]
                    )
                
                if category:
                    query = query.filter(
                        Income.category == category
                    )
                
                count = query.delete()
                db.session.commit()
                flash(f'成功清理 {count} 条记录', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'清理失败：{str(e)}', 'error')
        
        return redirect(url_for('main.data_cleanup'))
    
    # GET请求，返回数据清理页面
    return render_template('cleanup.html', stats=stats)

@main.route('/financial_health', methods=['GET'])
def financial_health():
    """财务健康分析"""
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    # 计算财务指标
    metrics = {
            'surplus_rate': 0,
            'debt_rate': 0,
            'net_worth_growth': 0,
            'cash_flow_ratio': 0,
            'roe': 0
        }
    
    # 查询当年数据
    incomes_this_year = Income.query.filter(db.extract('year', Income.date) == year).all()
    expenses_this_year = Expense.query.filter(db.extract('year', Expense.date) == year).all()
    
    # 获取当年资产数据 - 仅使用年度周期或最新的月度数据
    assets_query_this_year = Asset.query.filter(
        db.extract('year', Asset.update_date) == year
    ).order_by(Asset.name, Asset.type, Asset.owner, Asset.update_date.desc())
    
    # 按年度周期筛选资产数据（如果有年度数据则使用，否则使用最新的月度数据）
    assets_dict_this_year = {}
    for asset in assets_query_this_year:
        key = (asset.name, asset.type, asset.owner)
        if key not in assets_dict_this_year:
            assets_dict_this_year[key] = asset
            # 如果是年度数据，直接跳出循环
            if asset.period_type == 'annual':
                continue
    assets_this_year = list(assets_dict_this_year.values())
    
    # 获取当年负债数据 - 仅使用年度周期或最新的月度数据
    liabilities_query_this_year = Liability.query.filter(
        db.extract('year', Liability.update_date) == year
    ).order_by(Liability.name, Liability.type, Liability.owner, Liability.update_date.desc())
    
    # 按年度周期筛选负债数据
    liabilities_dict_this_year = {}
    for liability in liabilities_query_this_year:
        key = (liability.name, liability.type, liability.owner)
        if key not in liabilities_dict_this_year:
            liabilities_dict_this_year[key] = liability
            # 如果是年度数据，直接跳出循环
            if liability.period_type == 'annual':
                continue
    liabilities_this_year = list(liabilities_dict_this_year.values())
    
    # 查询上年数据
    incomes_last_year = Income.query.filter(db.extract('year', Income.date) == year-1).all()
    expenses_last_year = Expense.query.filter(db.extract('year', Expense.date) == year-1).all()
    
    # 获取上年资产数据
    assets_query_last_year = Asset.query.filter(
        db.extract('year', Asset.update_date) == year-1
    ).order_by(Asset.name, Asset.type, Asset.owner, Asset.update_date.desc())
    
    assets_dict_last_year = {}
    for asset in assets_query_last_year:
        key = (asset.name, asset.type, asset.owner)
        if key not in assets_dict_last_year:
            assets_dict_last_year[key] = asset
            if asset.period_type == 'annual':
                continue
    assets_last_year = list(assets_dict_last_year.values())
    
    # 获取上年负债数据
    liabilities_query_last_year = Liability.query.filter(
        db.extract('year', Liability.update_date) == year-1
    ).order_by(Liability.name, Liability.type, Liability.owner, Liability.update_date.desc())
    
    liabilities_dict_last_year = {}
    for liability in liabilities_query_last_year:
        key = (liability.name, liability.type, liability.owner)
        if key not in liabilities_dict_last_year:
            liabilities_dict_last_year[key] = liability
            if liability.period_type == 'annual':
                continue
    liabilities_last_year = list(liabilities_dict_last_year.values())
    
    # 计算当年收入和支出
    total_income_this_year = sum(income.amount for income in incomes_this_year)
    total_expense_this_year = sum(expense.amount for expense in expenses_this_year)
    total_assets_this_year = sum(asset.amount for asset in assets_this_year)
    total_liabilities_this_year = sum(liability.amount for liability in liabilities_this_year)
    net_worth_this_year = total_assets_this_year - total_liabilities_this_year
    
    # 计算上年净资产
    total_assets_last_year = sum(asset.amount for asset in assets_last_year)
    total_liabilities_last_year = sum(liability.amount for liability in liabilities_last_year)
    net_worth_last_year = total_assets_last_year - total_liabilities_last_year
    
    # 计算经营活动现金净流量
    operating_cash_flow = total_income_this_year - total_expense_this_year
    
    # 计算结余率
    if total_income_this_year > 0:
        metrics['surplus_rate'] = (total_income_this_year - total_expense_this_year) / total_income_this_year
    
    # 计算偿债率
    if total_assets_this_year > 0:
        metrics['debt_rate'] = total_liabilities_this_year / total_assets_this_year
    
    # 计算净资产增长率
        if net_worth_last_year > 0:
            metrics['net_worth_growth'] = (net_worth_this_year - net_worth_last_year) / net_worth_last_year

        # 计算净资产收益率 (ROE)
        net_income_this_year = total_income_this_year - total_expense_this_year
        average_net_worth = (net_worth_last_year + net_worth_this_year) / 2
        if average_net_worth > 0:
            metrics['roe'] = (net_income_this_year / average_net_worth) * 100
        else:
            metrics['roe'] = 0

        # 计算现金流比率
        if total_liabilities_this_year > 0:
            metrics['cash_flow_ratio'] = operating_cash_flow / total_liabilities_this_year
    
    # 计算健康得分
    health_score = 0
    
    # 结余率 (30%)
    if metrics['surplus_rate'] >= 0.3:
        health_score += 30
    elif metrics['surplus_rate'] >= 0.1:
        health_score += 20
    elif metrics['surplus_rate'] >= 0:
        health_score += 10
    
    # 偿债率 (30%)
    if metrics['debt_rate'] < 0.5:
        health_score += 30
    elif metrics['debt_rate'] < 0.7:
        health_score += 20
    elif metrics['debt_rate'] < 0.85:
        health_score += 10
    
    # 净资产增长率 (20%)
    if metrics['net_worth_growth'] >= 0.1:
        health_score += 20
    elif metrics['net_worth_growth'] >= 0.05:
        health_score += 15
    elif metrics['net_worth_growth'] >= 0:
        health_score += 10
    
    # 现金流比率 (20%)
    if metrics['cash_flow_ratio'] >= 0.5:
        health_score += 20
    elif metrics['cash_flow_ratio'] >= 0.3:
        health_score += 15
    elif metrics['cash_flow_ratio'] >= 0:
        health_score += 10
    
    # 确定健康等级
    if health_score >= 80:
        health_level = '优秀'
    elif health_score >= 60:
        health_level = '良好'
    elif health_score >= 40:
        health_level = '一般'
    else:
        health_level = '需要改善'
    
    return render_template('financial_health.html',
                           year=year,
                           metrics=metrics,
                           health_score=health_score,
                           health_level=health_level)

@main.route('/dashboard', methods=['GET'])
def dashboard():
    """仪表盘 - 财务概览与图表"""
    from datetime import datetime
    # 获取筛选参数
    year = request.args.get('year', datetime.now().year)
    year = int(year)
    
    month = request.args.get('month')
    month = int(month) if month is not None and month != 'all' else None
    
    # Calculate year range for dropdown
    current_year = datetime.now().year
    year_range = range(current_year - 5, current_year + 2)
    
    # 构建查询条件
    income_query = Income.query.filter(db.extract('year', Income.date) == year)
    expense_query = Expense.query.filter(db.extract('year', Expense.date) == year)
    
    # 添加月份筛选
    if month is not None:
        income_query = income_query.filter(db.extract('month', Income.date) == month)
        expense_query = expense_query.filter(db.extract('month', Expense.date) == month)
    
    # 查询数据
    incomes = income_query.all()
    expenses = expense_query.all()
    
    # 计算KPI指标
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    net_surplus = total_income - total_expense
    
    # 储蓄目标进度（默认年目标12万，如果是月度则按比例调整）
    base_savings_goal = 120000
    savings_goal = base_savings_goal / 12 if month is not None else base_savings_goal
    savings_progress = min((net_surplus / savings_goal) * 100, 100) if savings_goal > 0 else 0
    
    # 支出分类汇总
    expense_categories = {}
    for expense in expenses:
        if expense.category not in expense_categories:
            expense_categories[expense.category] = 0
        expense_categories[expense.category] += expense.amount
    
    # 准备饼图数据
    pie_data = {
        'labels': list(expense_categories.keys()),
        'values': list(expense_categories.values())
    }
    
    # 准备收入支出对比柱状图数据
    # 获取所有月份的数据
    monthly_data = []
    months = range(1, 13) if month is None else [month]
    
    for m in months:
        # 计算该月份的收入和支出
        monthly_income = sum(income.amount for income in incomes if income.date.month == m)
        monthly_expense = sum(expense.amount for expense in expenses if expense.date.month == m)
        
        month_name = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'][m-1]
        monthly_data.append({
            'month': month_name,
            'income': monthly_income,
            'expense': monthly_expense
        })
    
    bar_chart_data = {
        'months': [item['month'] for item in monthly_data],
        'incomes': [item['income'] for item in monthly_data],
        'expenses': [item['expense'] for item in monthly_data]
    }
    
    return render_template('dashboard.html',
                           year=year,
                           month=month,
                           year_range=year_range,
                           total_income=total_income,
                           total_expense=total_expense,
                           net_surplus=net_surplus,
                           savings_goal=savings_goal,
                           savings_progress=savings_progress,
                           pie_data=pie_data,
                           bar_chart_data=bar_chart_data)


@main.route('/comparison_chart', methods=['GET'])
def comparison_chart():
    """生成收入支出结余对比图表"""
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')  # 非GUI后端
    import matplotlib.pyplot as plt
    import os
    
    # 获取所有年份的数据
    all_income = Income.query.all()
    all_expenses = Expense.query.all()
    
    # 转换为DataFrame以便处理
    income_df = pd.DataFrame([(i.date.year, i.amount) for i in all_income], columns=['year', 'amount'])
    expense_df = pd.DataFrame([(e.date.year, e.amount) for e in all_expenses], columns=['year', 'amount'])
    
    # 按年份分组求和
    income_by_year = income_df.groupby('year')['amount'].sum().reset_index()
    expense_by_year = expense_df.groupby('year')['amount'].sum().reset_index()
    
    # 合并数据
    merged_df = pd.merge(income_by_year, expense_by_year, on='year', how='outer', suffixes=('_income', '_expense'))
    merged_df = merged_df.fillna(0)
    merged_df = merged_df.sort_values('year')
    
    # 计算结余
    merged_df['surplus'] = merged_df['amount_income'] - merged_df['amount_expense']
    
    # 准备图表数据
    years = merged_df['year'].tolist()
    incomes = merged_df['amount_income'].tolist()
    expenses = merged_df['amount_expense'].tolist()
    surpluses = merged_df['surplus'].tolist()
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制收入和支出 - 使用新的色彩方案
    ax.bar(years, incomes, width=0.3, label='收入', color='#007bff')  # 柔和海洋蓝
    ax.bar(years, [-expense for expense in expenses], width=0.3, label='支出', color='#ff6b6b')  # 珊瑚红
    
    # 绘制结余折线 - 使用绿色
    ax.plot(years, surpluses, label='结余', color='#28a745', marker='o', linewidth=2)
    
    ax.set_xlabel('年份')
    ax.set_ylabel('金额(元)')
    ax.set_title('收入支出结余对比')
    ax.legend()
    
    # 在柱子上显示数值
    # 在柱子上显示数值
    for i, year in enumerate(years):
        income = incomes[i]
        expense = expenses[i]
        surplus = surpluses[i]
        
        ax.text(i, income + income * 0.01, f'{income:,.0f}', ha='center', va='bottom', color='#007bff', fontsize=9)  # 海洋蓝
        ax.text(i, -expense - expense * 0.01, f'{expense:,.0f}', ha='center', va='top', color='#ff6b6b', fontsize=9)  # 珊瑚红
        ax.text(i, surplus + surplus * 0.02, f'{surplus:,.0f}', ha='center', va='bottom' if surplus >= 0 else 'top', color='#28a745', fontsize=9)  # 绿色
    
    plt.tight_layout()
    
    # 保存图表到静态文件夹
    chart_path = os.path.join(current_app.root_path, 'static', 'charts', 'income_expense_surplus.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    
    # 返回图表URL
    chart_url = url_for('static', filename='charts/income_expense_surplus.png')
    return render_template('comparison_chart.html', chart_url=chart_url, years=years, incomes=incomes, expenses=expenses, surpluses=surpluses)
