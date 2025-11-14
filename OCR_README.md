# 本地OCR功能使用说明

## 概述
本系统集成了本地LMstudio运行的DeepSeek-OCR服务，支持银行账单图像的自动识别与导入。

## 前置条件
1. **安装LMstudio**：从[LMstudio官网](https://lmstudio.ai/)下载并安装
2. **下载OCR模型**：在LMstudio中搜索并下载 `deepseek-ai/DeepSeek-OCR-V2-Instruct-GGUF` 模型
3. **启动OCR服务**：
   - 选择下载好的模型
   - 设置模型名称为 `deepseek-ocr`
   - 点击「Start Server」，默认端口：`http://localhost:1234`

## 服务配置
### LMstudio服务配置
- **模型名称**：deepseek-ocr
- **端口**：1234
- **上下文长度**：建议设置为8192

## 使用方法
### 1. 启动系统
```bash
python run.py
```

### 2. 上传图像
- 访问 `http://127.0.0.1:5000/import/image`
- 选择「收入」或「支出」类型
- 上传银行账单图像（支持JPG/PNG格式）
- 点击「上传并识别」

### 3. 自动解析与导入
系统会自动：
1. 将图像转换为base64格式
2. 发送到本地LMstudio OCR服务
3. 解析OCR结果为结构化JSON
4. 导入数据库并生成财务记录

## API调用格式
系统使用OpenAI-like格式调用本地OCR服务：

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ocr",
    "messages": [
        {
            "role": "system",
            "content": "你是一个专业的银行账单解析专家..."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请识别这张银行账单"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
    ],
    "temperature": 0.7,
    "max_tokens": -1,
    "stream": false
}'
```

## 自定义配置
### 修改OCR提示词
在 `app/utils/ocr.py` 中的 `analyze_bank_statement` 函数可以自定义系统提示词。

### 修改服务地址
在 `app/utils/ocr.py` 中修改默认API地址：
```python
ocr_client = LocalDeepSeekOCR(api_url="http://localhost:1234/v1/chat/completions")
```

## 故障排除
### 常见错误
1. **API连接失败**：
   - 检查LMstudio服务是否已启动
   - 检查端口是否正确（默认1234）

2. **OCR解析失败**：
   - 确保图像清晰
   - 确保图像是标准的银行账单格式
   - 调整模型的上下文长度

3. **JSON解析错误**：
   - 检查DeepSeek-OCR的输出格式
   - 调整提示词要求严格的JSON格式

### 调试方法
运行测试脚本检查OCR服务状态：
```bash
python test_ocr.py
```

## 扩展功能
- **批量处理**：支持多图像上传
- **模板定制**：针对不同银行提供解析模板
- **人工修正**：识别后允许人工修正数据
- **格式优化**：自动分类交易类型

通过本地OCR服务，您可以实现**全程隐私安全的银行账单自动识别与导入**！
