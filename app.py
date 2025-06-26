from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv
import bcrypt
from sqlalchemy import func, and_
import re
import csv
from io import TextIOWrapper

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:081311@localhost/library_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)  # 改为password_hash以匹配数据库
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'admin'
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=True)
    admin_id = db.Column(db.String(20), db.ForeignKey('administrators.admin_id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_password(password_hash, password):
    """检查密码是否匹配"""
    try:
        # 尝试使用bcrypt验证
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        # 如果bcrypt验证失败，尝试直接比较（用于测试）
        return password_hash == password

# 数据库模型（对应您的表结构）
class BookCategory(db.Model):
    __tablename__ = 'book_categories'
    category_code = db.Column(db.String(20), primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Book(db.Model):
    __tablename__ = 'books'
    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    publish_date = db.Column(db.Date)
    price = db.Column(db.Numeric(10, 2))
    category_code = db.Column(db.String(20), db.ForeignKey('book_categories.category_code'))
    location = db.Column(db.String(50))
    total_copies = db.Column(db.Integer, default=0)
    available_copies = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('正常', '遗失', '损坏', '下架'), default='正常')
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = db.relationship('BookCategory', backref='books', lazy='joined')

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('男', '女', '其他'))
    department = db.Column(db.String(50))
    major = db.Column(db.String(50))
    grade = db.Column(db.Integer)
    class_name = db.Column(db.String(50))
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    account_status = db.Column(db.Enum('正常', '挂失', '冻结'), default='正常')
    max_borrow_limit = db.Column(db.Integer, default=5)
    current_borrow_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Administrator(db.Model):
    __tablename__ = 'administrators'
    admin_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50))
    contact = db.Column(db.String(20))
    permission_level = db.Column(db.Enum('超级管理员', '普通管理员', '图书管理员'), default='图书管理员')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'
    borrow_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), db.ForeignKey('books.isbn'))
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'))
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    renew_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('借出', '已还', '逾期', '遗失'), default='借出')
    fine_amount = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    book = db.relationship('Book', backref='borrow_records', lazy='joined')
    student = db.relationship('Student', backref='borrow_records', lazy='joined')

class Reservation(db.Model):
    __tablename__ = 'reservations'
    reservation_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), db.ForeignKey('books.isbn'))
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'))
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('等待', '可取', '取消', '过期'), default='等待')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    book = db.relationship('Book', backref='reservations', lazy='joined')
    student = db.relationship('Student', backref='reservations', lazy='joined')

class BookReview(db.Model):
    __tablename__ = 'book_reviews'
    review_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), db.ForeignKey('books.isbn'))
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    review_time = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    book = db.relationship('Book', backref='reviews', lazy='joined')
    student = db.relationship('Student', backref='reviews', lazy='joined')

class FineRecord(db.Model):
    __tablename__ = 'fine_records'
    fine_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.String(255))
    payment_status = db.Column(db.Enum('未缴纳', '已缴纳', '部分缴纳'), default='未缴纳')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.String(20), db.ForeignKey('administrators.admin_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    student = db.relationship('Student', backref='fine_records', lazy='joined')
    admin = db.relationship('Administrator', backref='fine_records', lazy='joined')

# 系统日志模型
class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    operation_type = db.Column(db.String(50), nullable=False)
    operation_desc = db.Column(db.Text)
    operator_id = db.Column(db.String(20), db.ForeignKey('administrators.admin_id'))
    operation_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    status = db.Column(db.Enum('成功', '失败'), default='成功')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    operator = db.relationship('Administrator', backref='system_logs', lazy='joined')

# 系统设置模型
class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

# 日志写入工具函数
def write_log(operation_type, operation_desc, operator_id=None, status='成功', error_message=None, ip_address=None):
    log = SystemLog(
        operation_type=operation_type,
        operation_desc=operation_desc,
        operator_id=operator_id,
        status=status,
        error_message=error_message,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()

# 获取系统参数，带默认值
def get_setting(key, default=None):
    setting = SystemSetting.query.filter_by(key=key).first()
    return setting.value if setting else default

# 设置系统参数
def set_setting(key, value, description=None):
    setting = SystemSetting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = SystemSetting(key=key, value=value, description=description)
        db.session.add(setting)
    db.session.commit()

# 路由定义
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        user = User.query.filter_by(username=username).first()
        # 使用密码验证函数
        if user and check_password(user.password_hash, password) and user.role == user_type:
            login_user(user)
            flash('登录成功！', 'success')
            if user_type == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录！', 'info')
    return redirect(url_for('index'))

# 学生功能路由
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not current_user.role == 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    student = Student.query.filter_by(student_id=current_user.student_id).first()
    today = date.today()
    # 自动更新逾期状态并生成罚款
    overdue_borrows = BorrowRecord.query.filter(
        BorrowRecord.student_id == student.student_id,
        BorrowRecord.status == '借出',
        BorrowRecord.due_date < today
    ).all()
    for borrow in overdue_borrows:
        borrow.status = '逾期'
        fine_exists = FineRecord.query.filter(
            FineRecord.student_id == student.student_id,
            FineRecord.reason.like(f'%{borrow.isbn}%')
        ).first()
        if not fine_exists:
            overdue_days = (today - borrow.due_date).days
            fine = FineRecord(
                student_id=student.student_id,
                amount=overdue_days * 1.0,
                reason=f'图书逾期: {borrow.book.title}({borrow.isbn}) 逾期{overdue_days}天',
                payment_status='未缴纳',
                admin_id='A001'
            )
            db.session.add(fine)
    # 动态更新所有未缴纳逾期罚款金额
    for fine in FineRecord.query.filter_by(student_id=student.student_id, payment_status='未缴纳').all():
        isbn_match = re.search(r'\((\d{10,13})\)', fine.reason or '')
        isbn = isbn_match.group(1) if isbn_match else None
        borrow = BorrowRecord.query.filter_by(student_id=student.student_id, isbn=isbn).order_by(BorrowRecord.due_date.desc()).first() if isbn else None
        if borrow and borrow.status == '逾期':
            overdue_days = (today - borrow.due_date).days
            fine.amount = overdue_days * 1.0
    db.session.commit()
    # 查询当前借阅（含借出和逾期）
    current_borrows = BorrowRecord.query.filter(
        BorrowRecord.student_id == student.student_id,
        BorrowRecord.status.in_(['借出', '逾期'])
    ).order_by(BorrowRecord.borrow_date.desc()).all()
    reservations = Reservation.query.filter_by(
        student_id=student.student_id,
        status='等待'
    ).all()
    reviewed_isbns = set([r.isbn for r in BookReview.query.filter_by(student_id=student.student_id).all()])
    fines = FineRecord.query.filter_by(student_id=student.student_id).all()
    return render_template('student/dashboard.html', 
        student=student, 
        current_borrows=current_borrows,
        reservations=reservations,
        today=today,
        reviewed_isbns=reviewed_isbns,
        fines=fines)

@app.route('/student/books')
@login_required
def student_books():
    if not current_user.role == 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    # 获取查询参数
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Book.query.join(BookCategory)
    
    if search:
        query = query.filter(
            db.or_(
                Book.title.contains(search),
                Book.author.contains(search),
                Book.isbn.contains(search)
            )
        )
    
    if category:
        query = query.filter(Book.category_code == category)
    
    books = query.all()
    categories = BookCategory.query.all()
    
    return render_template('student/books.html', books=books, categories=categories)

@app.route('/student/book/<isbn>')
@login_required
def student_book_detail(isbn):
    if not current_user.role == 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    book = Book.query.get_or_404(isbn)
    reviews = BookReview.query.filter_by(isbn=isbn).all()
    # 基于分类的推荐：同分类下借阅量最多的5本书，排除当前图书
    rec_books = (
        db.session.query(Book, func.count(BorrowRecord.borrow_id).label('borrow_count'))
        .outerjoin(BorrowRecord, Book.isbn == BorrowRecord.isbn)
        .filter(Book.category_code == book.category_code, Book.isbn != isbn)
        .group_by(Book)
        .order_by(db.desc('borrow_count'))
        .limit(5)
        .all()
    )
    rec_books = [b[0] for b in rec_books]
    return render_template('student/book_detail.html', book=book, reviews=reviews, rec_books=rec_books)

@app.route('/student/borrow/<isbn>', methods=['POST'])
@login_required
def student_borrow_book(isbn):
    if not current_user.role == 'student':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    student = Student.query.filter_by(student_id=current_user.student_id).first()
    book = Book.query.get_or_404(isbn)
    
    # 检查借阅条件
    if student.account_status != '正常':
        return jsonify({'success': False, 'message': '账户状态异常，无法借阅！'})
    
    if student.current_borrow_count >= student.max_borrow_limit:
        return jsonify({'success': False, 'message': '已达到最大借阅数量！'})
    
    if book.available_copies <= 0:
        return jsonify({'success': False, 'message': '图书已无可借副本！'})
    
    # 创建借阅记录
    borrow_record = BorrowRecord(
        isbn=isbn,
        student_id=student.student_id,
        borrow_date=datetime.now().date(),
        due_date=datetime.now().date() + timedelta(days=30),
        status='借出'
    )
    
    db.session.add(borrow_record)
    
    # 更新图书和学生信息
    book.available_copies -= 1
    student.current_borrow_count += 1
    
    db.session.commit()
    
    flash('借阅成功！', 'success')
    return jsonify({'success': True, 'message': '借阅成功！'})

@app.route('/student/reserve/<isbn>', methods=['POST'])
@login_required
def student_reserve_book(isbn):
    if not current_user.role == 'student':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    student = Student.query.filter_by(student_id=current_user.student_id).first()
    book = Book.query.get_or_404(isbn)
    
    # 检查是否已有预约
    existing_reservation = Reservation.query.filter_by(
        isbn=isbn,
        student_id=student.student_id,
        status='等待'
    ).first()
    
    if existing_reservation:
        return jsonify({'success': False, 'message': '您已预约过此书！'})
    
    # 创建预约记录
    reservation = Reservation(
        isbn=isbn,
        student_id=student.student_id,
        status='等待'
    )
    
    db.session.add(reservation)
    db.session.commit()
    
    flash('预约成功！', 'success')
    return jsonify({'success': True, 'message': '预约成功！'})

@app.route('/student/history')
@login_required
def student_history():
    if not current_user.role == 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    student = Student.query.filter_by(student_id=current_user.student_id).first()
    today = date.today()
    fine_per_day = float(get_setting('fine_per_day', 1.0))
    # 处理所有逾期借阅，自动生成罚款
    overdue_borrows = BorrowRecord.query.filter(
        BorrowRecord.student_id == student.student_id,
        BorrowRecord.status.in_(['借出', '逾期']),
        BorrowRecord.due_date < today
    ).all()
    for borrow in overdue_borrows:
        # 只要当前是逾期状态
        if borrow.status != '逾期':
            borrow.status = '逾期'
        # 检查是否已有罚款
        fine_exists = FineRecord.query.filter(
            FineRecord.student_id == student.student_id,
            FineRecord.reason.like(f'%{borrow.isbn}%'),
            FineRecord.payment_status == '未缴纳'
        ).first()
        overdue_days = (today - borrow.due_date).days
        if overdue_days > 0 and not fine_exists:
            fine = FineRecord(
                student_id=student.student_id,
                amount=overdue_days * fine_per_day,
                reason=f'图书逾期: {borrow.book.title}({borrow.isbn}) 逾期{overdue_days}天',
                payment_status='未缴纳',
                admin_id='A001'
            )
            db.session.add(fine)
    # 动态更新所有未缴纳逾期罚款金额
    for fine in FineRecord.query.filter_by(student_id=student.student_id, payment_status='未缴纳').all():
        isbn_match = re.search(r'\((\d{10,13})\)', fine.reason or '')
        isbn = isbn_match.group(1) if isbn_match else None
        borrow = BorrowRecord.query.filter_by(student_id=student.student_id, isbn=isbn).order_by(BorrowRecord.due_date.desc()).first() if isbn else None
        if borrow and borrow.status == '逾期':
            overdue_days = (today - borrow.due_date).days
            fine.amount = overdue_days * fine_per_day
    db.session.commit()
    history = BorrowRecord.query.filter_by(student_id=student.student_id).order_by(BorrowRecord.borrow_date.desc()).all()
    reviewed_isbns = set([r.isbn for r in BookReview.query.filter_by(student_id=student.student_id).all()])
    return render_template('student/history.html', history=history, reviewed_isbns=reviewed_isbns, today=today)

@app.route('/student/fines')
@login_required
def student_fines():
    if not current_user.role == 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    student = Student.query.filter_by(student_id=current_user.student_id).first()
    fines = FineRecord.query.filter_by(student_id=student.student_id).order_by(FineRecord.created_date.desc()).all()
    # 罚款与图书信息关联
    fine_infos = []
    for fine in fines:
        # 尝试从reason中提取ISBN
        isbn_match = re.search(r'\((\d{10,13})\)', fine.reason or '')
        isbn = isbn_match.group(1) if isbn_match else None
        book = Book.query.get(isbn) if isbn else None
        fine_infos.append({'fine': fine, 'book': book})
    return render_template('student/fines.html', fine_infos=fine_infos)

@app.route('/student/renew/<int:borrow_id>', methods=['POST'])
@login_required
def student_renew_book(borrow_id):
    if not current_user.role == 'student':
        return jsonify({'success': False, 'message': '权限不足！'})
    borrow = BorrowRecord.query.get_or_404(borrow_id)
    if borrow.student_id != current_user.student_id:
        return jsonify({'success': False, 'message': '只能续借自己的图书！'})
    if borrow.status != '借出':
        return jsonify({'success': False, 'message': '仅可续借"借出"状态的图书！'})
    today = date.today()
    if borrow.due_date < today:
        return jsonify({'success': False, 'message': '逾期图书不可续借！'})
    if borrow.renew_count >= 1:
        return jsonify({'success': False, 'message': '每本书最多可续借1次！'})
    # 续借操作
    borrow.due_date = borrow.due_date + timedelta(days=30)
    borrow.renew_count += 1
    db.session.commit()
    return jsonify({'success': True, 'message': '续借成功，应还日期已顺延30天！'})

# 管理员功能路由
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    # 统计信息
    total_books = Book.query.count()
    total_students = Student.query.count()
    total_borrows = BorrowRecord.query.filter_by(status='借出').count()
    overdue_books = BorrowRecord.query.filter(
        BorrowRecord.status == '借出',
        BorrowRecord.due_date < datetime.now().date()
    ).count()
    
    return render_template('admin/dashboard.html',
                         total_books=total_books,
                         total_students=total_students,
                         total_borrows=total_borrows,
                         overdue_books=overdue_books)

@app.route('/admin/books')
@login_required
def admin_books():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    books = Book.query.all()
    return render_template('admin/books.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def admin_add_book():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        book = Book(
            isbn=request.form['isbn'],
            title=request.form['title'],
            author=request.form['author'],
            publisher=request.form['publisher'],
            publish_date=datetime.strptime(request.form['publish_date'], '%Y-%m-%d').date(),
            price=float(request.form['price']),
            category_code=request.form['category_code'],
            location=request.form['location'],
            total_copies=int(request.form['total_copies']),
            available_copies=int(request.form['total_copies']),
            description=request.form['description']
        )
        
        db.session.add(book)
        db.session.commit()
        
        flash('图书添加成功！', 'success')
        return redirect(url_for('admin_books'))
    
    categories = BookCategory.query.all()
    return render_template('admin/add_book.html', categories=categories)

@app.route('/admin/students')
@login_required
def admin_students():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    students = Student.query.all()
    return render_template('admin/students.html', students=students)

@app.route('/admin/borrows')
@login_required
def admin_borrows():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    borrows = BorrowRecord.query.all()
    return render_template('admin/borrows.html', borrows=borrows, today=date.today())

@app.route('/admin/return/<int:borrow_id>', methods=['POST'])
@login_required
def admin_return_book(borrow_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    borrow_record = BorrowRecord.query.get_or_404(borrow_id)
    book = Book.query.get(borrow_record.isbn)
    student = Student.query.get(borrow_record.student_id)
    
    # 更新借阅记录
    borrow_record.status = '已还'
    borrow_record.return_date = datetime.now().date()
    
    # 更新图书和学生信息
    book.available_copies += 1
    student.current_borrow_count -= 1
    
    db.session.commit()
    
    flash('归还成功！', 'success')
    return jsonify({'success': True, 'message': '归还成功！'})

@app.route('/admin/books/import', methods=['POST'])
@login_required
def admin_import_books():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    if 'csv_file' not in request.files:
        flash('请选择文件！', 'error')
        return redirect(url_for('admin_books'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('请选择文件！', 'error')
        return redirect(url_for('admin_books'))
    
    if file and file.filename.endswith('.csv'):
        try:
            # 读取CSV文件
            stream = TextIOWrapper(file.stream._file, encoding='utf-8')
            csv_reader = csv.DictReader(stream)
            
            success_count = 0
            error_count = 0
            
            for row in csv_reader:
                try:
                    # 检查ISBN是否已存在
                    existing_book = Book.query.filter_by(isbn=row['isbn']).first()
                    if existing_book:
                        error_count += 1
                        continue
                    
                    # 创建新图书
                    book = Book(
                        isbn=row['isbn'],
                        title=row['title'],
                        author=row['author'],
                        publisher=row['publisher'],
                        category_code=row.get('category_code'),
                        location=row.get('location', ''),
                        total_copies=int(row.get('total_copies', 1)),
                        available_copies=int(row.get('total_copies', 1)),
                        description=row.get('description', ''),
                        price=float(row.get('price', 0)) if row.get('price') else None
                    )
                    
                    if row.get('publish_date'):
                        book.publish_date = datetime.strptime(row['publish_date'], '%Y-%m-%d').date()
                    
                    db.session.add(book)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
            
            db.session.commit()
            flash(f'导入完成！成功：{success_count}本，失败：{error_count}本', 'success')
            
        except Exception as e:
            flash(f'导入失败：{str(e)}', 'error')
    
    return redirect(url_for('admin_books'))

# 图书详情查看
@app.route('/admin/book/<isbn>')
@login_required
def admin_book_detail(isbn):
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    book = Book.query.filter_by(isbn=isbn).first()
    if not book:
        flash('图书不存在！', 'error')
        return redirect(url_for('admin_books'))
    
    # 获取借阅记录
    borrow_records = BorrowRecord.query.filter_by(isbn=isbn).order_by(BorrowRecord.borrow_date.desc()).limit(10).all()
    
    # 获取评价记录
    reviews = BookReview.query.filter_by(isbn=isbn).order_by(BookReview.review_time.desc()).limit(10).all()
    
    # 获取预约记录
    reservations = Reservation.query.filter_by(isbn=isbn).order_by(Reservation.reservation_date.desc()).limit(10).all()
    
    return render_template('admin/book_detail.html', book=book, borrow_records=borrow_records, reviews=reviews, reservations=reservations)

# 图书编辑
@app.route('/admin/book/<isbn>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_book(isbn):
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    book = Book.query.filter_by(isbn=isbn).first()
    if not book:
        flash('图书不存在！', 'error')
        return redirect(url_for('admin_books'))
    
    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.author = request.form['author']
            book.publisher = request.form['publisher']
            book.category_code = request.form['category_code']
            book.location = request.form['location']
            book.description = request.form['description']
            book.status = request.form['status']
            
            if request.form.get('publish_date'):
                book.publish_date = datetime.strptime(request.form['publish_date'], '%Y-%m-%d').date()
            
            if request.form.get('price'):
                book.price = float(request.form['price'])
            
            # 更新总册数时，同时更新可借册数
            new_total = int(request.form['total_copies'])
            if new_total != book.total_copies:
                diff = new_total - book.total_copies
                book.total_copies = new_total
                book.available_copies += diff
            
            db.session.commit()
            flash('图书信息更新成功！', 'success')
            return redirect(url_for('admin_book_detail', isbn=isbn))
            
        except Exception as e:
            flash(f'更新失败：{str(e)}', 'error')
    
    categories = BookCategory.query.all()
    return render_template('admin/edit_book.html', book=book, categories=categories)

# 图书删除
@app.route('/admin/book/<isbn>', methods=['DELETE'])
@login_required
def admin_delete_book(isbn):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    book = Book.query.filter_by(isbn=isbn).first()
    if not book:
        return jsonify({'success': False, 'message': '图书不存在！'})
    
    try:
        # 检查是否有未归还的借阅
        active_borrows = BorrowRecord.query.filter_by(isbn=isbn, status='借出').count()
        if active_borrows > 0:
            return jsonify({'success': False, 'message': f'该图书还有{active_borrows}本未归还，无法删除！'})
        
        # 删除相关记录
        BorrowRecord.query.filter_by(isbn=isbn).delete()
        Reservation.query.filter_by(isbn=isbn).delete()
        BookReview.query.filter_by(isbn=isbn).delete()
        
        # 删除图书
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '图书删除成功！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

# 学生详情查看
@app.route('/admin/student/<student_id>')
@login_required
def admin_student_detail(student_id):
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        flash('学生不存在！', 'error')
        return redirect(url_for('admin_students'))
    
    # 获取借阅记录
    borrow_records = BorrowRecord.query.filter_by(student_id=student_id).order_by(BorrowRecord.borrow_date.desc()).all()
    
    # 获取预约记录
    reservations = Reservation.query.filter_by(student_id=student_id).order_by(Reservation.reservation_date.desc()).all()
    
    # 获取罚款记录
    fine_records = FineRecord.query.filter_by(student_id=student_id).order_by(FineRecord.created_date.desc()).all()
    
    # 获取评价记录
    reviews = BookReview.query.filter_by(student_id=student_id).order_by(BookReview.review_time.desc()).all()
    
    return render_template('admin/student_detail.html', student=student, borrow_records=borrow_records, 
                         reservations=reservations, fine_records=fine_records, reviews=reviews)

# 学生状态管理
@app.route('/admin/student/<student_id>/status', methods=['POST'])
@login_required
def admin_toggle_student_status(student_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({'success': False, 'message': '学生不存在！'})
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['正常', '挂失', '冻结']:
            return jsonify({'success': False, 'message': '无效的状态值！'})
        
        student.account_status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'学生状态已更新为{new_status}！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})

# 预约管理
@app.route('/admin/reservations')
@login_required
def admin_reservations():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    # 获取所有预约记录
    reservations = Reservation.query.join(Book).join(Student).order_by(Reservation.reservation_date.desc()).all()
    
    return render_template('admin/reservations.html', reservations=reservations)

# 预约审批
@app.route('/admin/reservation/<int:reservation_id>/approve', methods=['POST'])
@login_required
def admin_approve_reservation(reservation_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({'success': False, 'message': '预约记录不存在！'})
    
    try:
        # 检查图书是否有可借副本
        book = Book.query.filter_by(isbn=reservation.isbn).first()
        if book.available_copies > 0:
            reservation.status = '可取'
            book.available_copies -= 1
            db.session.commit()
            return jsonify({'success': True, 'message': '预约审批成功！'})
        else:
            return jsonify({'success': False, 'message': '图书暂无可借副本！'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'审批失败：{str(e)}'})

# 预约取消
@app.route('/admin/reservation/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def admin_cancel_reservation(reservation_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({'success': False, 'message': '预约记录不存在！'})
    
    try:
        reservation.status = '取消'
        db.session.commit()
        return jsonify({'success': True, 'message': '预约已取消！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'取消失败：{str(e)}'})

# 评价管理
@app.route('/admin/reviews')
@login_required
def admin_reviews():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    # 获取所有评价记录
    reviews = BookReview.query.join(Book).join(Student).order_by(BookReview.review_time.desc()).all()
    
    return render_template('admin/reviews.html', reviews=reviews)

# 删除评价
@app.route('/admin/review/<int:review_id>', methods=['DELETE'])
@login_required
def admin_delete_review(review_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    review = BookReview.query.get(review_id)
    if not review:
        return jsonify({'success': False, 'message': '评价记录不存在！'})
    
    try:
        db.session.delete(review)
        db.session.commit()
        return jsonify({'success': True, 'message': '评价删除成功！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

# 罚款管理
@app.route('/admin/fines')
@login_required
def admin_fines():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    # 获取所有罚款记录
    fines = FineRecord.query.join(Student).order_by(FineRecord.created_date.desc()).all()
    students = Student.query.all()
    
    return render_template('admin/fines.html', fines=fines, students=students)

# 添加罚款
@app.route('/admin/fine/add', methods=['GET', 'POST'])
@login_required
def admin_add_fine():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            student_id = request.form['student_id']
            amount = float(request.form['amount'])
            reason = request.form['reason']
            
            # 检查学生是否存在
            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                flash('学生不存在！', 'error')
                return redirect(url_for('admin_add_fine'))
            
            fine = FineRecord(
                student_id=student_id,
                amount=amount,
                reason=reason,
                admin_id=current_user.admin_id
            )
            
            db.session.add(fine)
            db.session.commit()
            
            flash('罚款记录添加成功！', 'success')
            return redirect(url_for('admin_fines'))
            
        except Exception as e:
            flash(f'添加失败：{str(e)}', 'error')
    
    students = Student.query.all()
    return render_template('admin/add_fine.html', students=students)

# 更新罚款状态
@app.route('/admin/fine/<int:fine_id>/status', methods=['POST'])
@login_required
def admin_update_fine_status(fine_id):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    fine = FineRecord.query.get(fine_id)
    if not fine:
        return jsonify({'success': False, 'message': '罚款记录不存在！'})
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['未缴纳', '已缴纳', '部分缴纳']:
            return jsonify({'success': False, 'message': '无效的状态值！'})
        
        fine.payment_status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': '罚款状态更新成功！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})

# 系统日志
@app.route('/admin/logs')
@login_required
def admin_logs():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))

    # 获取筛选参数
    operation_type = request.args.get('operation_type', '').strip()
    operator_id = request.args.get('operator_id', '').strip()
    status = request.args.get('status', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = SystemLog.query
    if operation_type:
        query = query.filter(SystemLog.operation_type.like(f'%{operation_type}%'))
    if operator_id:
        query = query.filter(SystemLog.operator_id == operator_id)
    if status:
        query = query.filter(SystemLog.status == status)
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(SystemLog.operation_time >= start_dt)
        except:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(SystemLog.operation_time <= end_dt)
        except:
            pass

    logs = query.order_by(SystemLog.operation_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    # 获取所有管理员用于筛选
    admins = Administrator.query.all()
    return render_template('admin/logs.html', logs=logs, admins=admins, 
        operation_type=operation_type, operator_id=operator_id, status=status, start_date=start_date, end_date=end_date)

# 统计报表
@app.route('/admin/reports')
@login_required
def admin_reports():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    # 统计信息
    total_books = Book.query.count()
    total_students = Student.query.count()
    total_borrows = BorrowRecord.query.filter_by(status='借出').count()
    overdue_books = BorrowRecord.query.filter(
        BorrowRecord.status == '借出',
        BorrowRecord.due_date < date.today()
    ).count()
    
    # 分类统计
    category_stats = db.session.query(
        BookCategory.category_name,
        func.count(Book.isbn).label('book_count')
    ).join(Book).group_by(BookCategory.category_code).all()
    
    # 院系借阅统计
    dept_stats = db.session.query(
        Student.department,
        func.count(BorrowRecord.borrow_id).label('borrow_count')
    ).join(BorrowRecord).group_by(Student.department).all()
    all_borrow_count = sum([d[1] for d in dept_stats])
    
    # 热门图书
    popular_books = db.session.query(
        Book.title,
        func.count(BorrowRecord.borrow_id).label('borrow_count')
    ).join(BorrowRecord).group_by(Book.isbn).order_by(func.count(BorrowRecord.borrow_id).desc()).limit(10).all()
    
    return render_template('admin/reports.html', 
                         total_books=total_books,
                         total_students=total_students,
                         total_borrows=total_borrows,
                         overdue_books=overdue_books,
                         category_stats=category_stats,
                         dept_stats=dept_stats,
                         all_borrow_count=all_borrow_count,
                         popular_books=popular_books)

# 图书分类管理
@app.route('/admin/categories')
@login_required
def admin_categories():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    categories = BookCategory.query.all()
    return render_template('admin/categories.html', categories=categories)

# 添加分类
@app.route('/admin/category/add', methods=['POST'])
@login_required
def admin_add_category():
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    try:
        category_code = request.form['category_code']
        category_name = request.form['category_name']
        category_description = request.form.get('category_description', '')
        
        # 检查分类代码是否已存在
        existing = BookCategory.query.filter_by(category_code=category_code).first()
        if existing:
            return jsonify({'success': False, 'message': '分类代码已存在！'})
        
        category = BookCategory(
            category_code=category_code,
            category_name=category_name,
            category_description=category_description
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '分类添加成功！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})

# 删除分类
@app.route('/admin/category/<category_code>', methods=['DELETE'])
@login_required
def admin_delete_category(category_code):
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': '权限不足！'})
    
    category = BookCategory.query.filter_by(category_code=category_code).first()
    if not category:
        return jsonify({'success': False, 'message': '分类不存在！'})
    
    try:
        # 检查是否有图书使用此分类
        book_count = Book.query.filter_by(category_code=category_code).count()
        if book_count > 0:
            return jsonify({'success': False, 'message': f'该分类下还有{book_count}本图书，无法删除！'})
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '分类删除成功！'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.role == 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    # 支持的参数
    param_defs = [
        {'key': 'max_borrow', 'label': '最大借阅量', 'type': 'number', 'default': 5, 'description': '每个学生最多可借图书数量'},
        {'key': 'borrow_days', 'label': '借阅期限(天)', 'type': 'number', 'default': 30, 'description': '每本书的借阅天数'},
        {'key': 'fine_per_day', 'label': '逾期每日罚款', 'type': 'number', 'step': '0.01', 'default': 1.0, 'description': '每逾期一天罚款金额'}
    ]
    if request.method == 'POST':
        for param in param_defs:
            value = request.form.get(param['key'])
            if value is not None:
                set_setting(param['key'], value, param['description'])
        flash('系统参数已保存！', 'success')
        return redirect(url_for('admin_settings'))
    # 读取参数
    params = []
    for param in param_defs:
        value = get_setting(param['key'], param['default'])
        params.append({**param, 'value': value})
    return render_template('admin/settings.html', params=params)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 