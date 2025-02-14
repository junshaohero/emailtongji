# AI Domain Name Checker

一个用于查找未注册的三字母.ai域名的Web工具。

## 功能特点

- 自动生成所有可能的三字母组合
- 检查域名是否已被注册
- 并发处理多个域名查询
- 简洁的用户界面
- 支持查看域名详细信息

## 安装说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

3. 打开浏览器访问：
```
http://localhost:5000
```

## 使用说明

1. 点击"开始查询"按钮
2. 等待查询结果显示
3. 点击"查看详情"可以查看具体域名的注册信息

## 注意事项

- 查询过程可能需要一些时间，请耐心等待
- 为了避免API限制，查询采用了限速机制
- 查询结果仅供参考，建议在正式注册前再次确认域名状态
