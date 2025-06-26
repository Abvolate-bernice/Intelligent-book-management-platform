


# 智能图书管理系统

## 项目简介

这是一个基于数据库系统原理设计的现代化图书管理系统，采用Flask + MySQL技术栈，实现了完整的图书借阅、预约、管理功能。
## 系统演示

<video src="demo.mp4" controls>
  你的浏览器不支持 video 标签
</video>

## 系统特色

### 🗄️ 数据库设计
- **11个核心表**：完整的图书管理业务模型
- **4个触发器**：自动更新库存、计算罚款、管理账户状态
- **3个存储过程**：批量处理、统计报表、自动提醒
- **5个智能视图**：热门图书、院系统计、逾期监控等

### ⚡ 自动化功能
- 借阅时自动更新图书可借数量和学生借阅计数
- 归还时自动计算逾期罚款
- 超阈值自动冻结学生账户
- 定期发送逾期提醒

### 🎯 用户功能
- **学生功能**：图书查询、在线借阅、预约管理、评价评论
- **管理员功能**：图书管理、学生管理、借阅处理、统计报表

## 技术栈

- **后端**：Python Flask
- **数据库**：MySQL 8.0+
- **前端**：Bootstrap 5 + jQuery
- **认证**：Flask-Login
- **ORM**：SQLAlchemy

## 安装部署

### 1. 环境要求
- Python 3.8+
- MySQL 8.0+
- pip

### 2. 克隆项目
```bash
git clone <repository-url>
cd library-system
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库配置
1. 创建MySQL数据库
2. 执行数据库脚本：
```bash
mysql -u root -p < database.sql
mysql -u root -p < data.sql
mysql -u root -p < init_users.sql
```

### 5. 配置环境变量
创建 `.env` 文件：
```
DATABASE_URL=mysql+pymysql://username:password@localhost/library_system
SECRET_KEY=your-secret-key-here
```

### 6. 运行应用
```bash
python app.py
```

访问 http://localhost:5000

## 测试账号

### 学生账号
- 用户名：3230608024，密码：123456

### 管理员账号
- 用户名：A001，密码：123456

## 数据库结构

### 核心表
1. **book_categories** - 图书分类
2. **books** - 图书信息
3. **students** - 学生信息
4. **administrators** - 管理员信息
5. **borrow_records** - 借阅记录
6. **reservations** - 图书预约
7. **book_reviews** - 图书评价
8. **fine_records** - 罚款记录
9. **system_logs** - 系统日志
10. **notification_logs** - 通知日志
11. **users** - 用户账户

### 触发器
- `after_borrow_insert` - 借阅时更新库存
- `after_borrow_update_return` - 归还时更新库存
- `calculate_fine_on_return` - 自动计算罚款
- `update_student_status_on_fine` - 自动冻结账户

### 存储过程
- `initialize_student_accounts` - 学期初账户初始化
- `generate_circulation_report` - 生成流通统计报表
- `send_overdue_notifications` - 发送逾期提醒

### 视图
- `popular_books` - 热门图书排行
- `department_borrow_stats` - 院系借阅统计
- `book_overdue_status` - 逾期情况监控
- `reservation_queue` - 预约队列管理
- `student_borrow_history` - 学生借阅历史

## 功能模块

### 学生功能
- ✅ 多条件图书查询
- ✅ 图书详情查看
- ✅ 在线借阅预约
- ✅ 个人借阅历史
- ✅ 图书评价评论
- ✅ 账户状态查看

### 管理员功能
- ✅ 图书信息管理
- ✅ 学生账户管理
- ✅ 借还书处理
- ✅ 预约队列管理
- ✅ 统计报表查看
- ✅ 系统参数设置

## 项目结构

```
library-system/
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖
├── database.sql          # 数据库结构脚本
├── data.sql             # 示例数据脚本
├── init_users.sql       # 用户初始化脚本
├── README.md            # 项目说明
├── templates/           # HTML模板
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── student/
│   │   ├── dashboard.html
│   │   ├── books.html
│   │   └── book_detail.html
│   └── admin/
│       ├── dashboard.html
│       ├── books.html
│       ├── add_book.html
│       ├── students.html
│       └── borrows.html
└── static/              # 静态文件
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 开发说明

### 数据库设计原则
- 遵循3NF范式设计
- 合理使用外键约束
- 适当的索引优化
- 触发器保证数据一致性

### 代码规范
- Python代码遵循PEP 8
- HTML使用Bootstrap 5规范
- JavaScript使用ES6+语法
- 数据库使用标准SQL

## 课程设计要点

### 数据库系统原理应用
1. **关系模型设计**：完整的ER图和关系模式
2. **SQL语言应用**：DDL、DML、DCL、DQL
3. **触发器机制**：自动化业务逻辑
4. **存储过程**：复杂业务处理
5. **视图设计**：数据抽象和简化
6. **索引优化**：查询性能提升
7. **事务管理**：数据一致性保证

### 系统设计亮点
- 完整的业务流程设计
- 自动化处理机制
- 用户友好的界面
- 响应式设计
- 安全性考虑

## 许可证

本项目仅用于数据库系统原理课程设计，请勿用于商业用途。

## 联系方式

署名：江苏大学-小鸡快跑 2025.5
