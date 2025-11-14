# 家庭财务健康跟踪系统

一个基于Python Flask的家庭财务健康跟踪与分析系统，支持导入财务数据、生成财务报表并分析财务健康状况。

## 功能特性

1. **数据导入**：支持CSV格式的收入、支出、资产、负债数据导入，以及银行账单图像OCR自动识别导入
2. **财务报表**：
   - 收入利润表：按年份显示收入、支出和结余情况
   - 资产负债表：显示资产、负债和净资产状况
   - 现金流量表：记录现金流入流出情况
3. **财务健康分析**：
   - 结余率：分析储蓄能力
   - 偿债率：评估负债风险
   - 净资产增长率：显示资产增值情况
   - 现金流比率：评估现金流动性
   - 综合健康评分：提供直观的财务健康状况

## 技术栈

- **后端**：Python Flask
- **数据库**：SQLite (支持扩展到MySQL/PostgreSQL)
- **前端**：HTML/CSS/JavaScript (原生)
- **数据处理**：Pandas
- **ORM**：SQLAlchemy
- **迁移工具**：Flask-Migrate

## 项目结构

```
family_finance/
├── app/
│   ├── __init__.py          # 应用初始化
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据模型
│   ├── views.py            # 路由和视图函数
│   ├── static/             # 静态文件
│   │   ├── charts/         # 图表静态文件
│   │   └── css/            # CSS样式文件
│   ├── templates/          # HTML模板
│   │   ├── index.html      # 首页
│   │   ├── import.html     # 数据导入页面
│   │   ├── import_image.html # 图像导入页面
│   │   ├── income_statement.html  # 收入利润表
│   │   ├── balance_sheet.html     # 资产负债表
│   │   ├── cash_flow.html         # 现金流量表
│   │   ├── financial_health.html  # 财务健康分析
│   │   └── ocr_preview.html       # OCR识别预览页面
│   └── utils/              # 工具函数
│       └── ocr.py          # OCR识别工具
├── example_data/           # 示例数据文件
├── uploads/                # 上传文件目录（自动创建）
├── run.py                  # 应用入口
├── requirements.txt        # 依赖文件
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python run.py
```

### 3. 访问应用

打开浏览器访问：`http://127.0.0.1:5002`

## 使用说明

### 数据导入

#### CSV文件导入
1. 点击"数据导入"菜单
2. 选择数据类型（收入、支出、资产、负债）
3. 上传对应的CSV文件
4. 点击"导入数据"

#### OCR图像导入
系统支持本地LMstudio运行的qwen/qwen3-vl-4b服务，实现银行账单图像的自动识别与导入。

**前置条件**：
1. 从[LMstudio官网](https://lmstudio.ai/)下载并安装LMstudio
2. 在LMstudio中搜索并下载 `qwen/qwen3-vl-4b` 模型（默认）或其他支持OCR的多模态模型（如 `deepseek-ai/DeepSeek-OCR-V2-Instruct-GGUF`）
3. 在LMstudio中启动服务，默认地址为 `http://localhost:1234/v1/chat/completions`

**使用方法**：
1. 点击"OCR图像导入"菜单
2. 选择报告月份、数据类型和所有者
3. 上传银行账单图像（支持JPG/PNG格式）
4. 点击"上传并识别"
5. 确认OCR识别结果后点击"确认导入"

### CSV文件格式

#### 收入/支出格式：
```csv
date,category,amount,source/payer,description
2023-01-15,工资,10000,我,1月份工资
2023-01-20,房租,3000,爱人,1月份房租
```

#### 资产/负债格式：
```csv
name,type,amount,owner,update_date,description
招商银行,银行存款,50000,我,2023-01-31,储蓄卡
房贷,房贷,500000,共同,2023-01-31,住房贷款
```

### 查看财务报表

1. 收入利润表：查看年度收入、支出和结余
2. 资产负债表：查看资产、负债和净资产情况
3. 现金流量表：查看现金流入流出明细
4. 财务健康分析：查看综合财务健康评分和各项指标

## 示例数据

项目提供了示例数据文件，位于 `example_data/` 目录下，包括：
- income_example.csv：收入示例数据
- expense_example.csv：支出示例数据
- asset_example.csv：资产示例数据
- liability_example.csv：负债示例数据

可以直接导入这些示例数据进行测试。

## 财务健康指标说明

1. **结余率**：(总收入 - 总支出) / 总收入 × 100%
   - 优秀：30%以上
   - 良好：10-30%
   - 需要改善：10%以下

2. **偿债率**：总负债 / 总资产 × 100%
   - 安全：50%以下
   - 警告：50-70%
   - 危险：70%以上

3. **净资产增长率**：(当年净资产 - 上年净资产) / 上年净资产 × 100%
   - 优秀：10%以上

4. **现金流比率**：经营活动现金净流量 / 总负债 × 100%
   - 安全：50%以上

## 配置

应用配置文件位于 `app/config.py`，可以修改以下参数：
- 数据库连接
- 上传文件大小限制
- 上传目录

## 开发

### 数据库迁移

```bash
# 初始化迁移
flask db init

# 创建迁移脚本
flask db migrate -m "create tables"

# 应用迁移
flask db upgrade
```

### 代码结构

- 数据模型：`app/models.py`
- 路由和业务逻辑：`app/views.py`
- 模板：`app/templates/`

## 扩展

系统可以轻松扩展以下功能：
- 添加更多财务指标和分析
- 生成图表可视化
- 导出报表功能
- 用户认证
- 移动端适配
- 多用户支持

## 许可证

MIT License
