-- ######################################################################
-- ############ 智能图书管理系统 - 完整数据库创建脚本 #################
-- ######################################################################

-- 1. 删除旧数据库（如果存在），以便重新开始一个干净的环境
DROP DATABASE IF EXISTS library_system;

-- 2. 创建数据库
CREATE DATABASE IF NOT EXISTS library_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_system;

-- ######################################################################
-- ########################### 表结构定义 #############################
-- ######################################################################

-- 3. 图书分类表 (根据3NF优化新增)
CREATE TABLE book_categories (
    category_code VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. 图书信息表
CREATE TABLE books (
    isbn VARCHAR(13) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher VARCHAR(100) NOT NULL,
    publish_date DATE,
    price DECIMAL(10,2),
    category_code VARCHAR(20), -- FK to book_categories
    location VARCHAR(50),
    total_copies INT NOT NULL DEFAULT 0,
    available_copies INT NOT NULL DEFAULT 0,
    status ENUM('正常', '遗失', '损坏', '下架') DEFAULT '正常',
    description TEXT,
    cover_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_code) REFERENCES book_categories(category_code)
);

-- 5. 学生信息表
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男', '女', '其他'),
    department VARCHAR(50),
    major VARCHAR(50),
    grade INT,
    class_name VARCHAR(50),
    contact VARCHAR(20),
    email VARCHAR(100),
    account_status ENUM('正常', '挂失', '冻结') DEFAULT '正常',
    max_borrow_limit INT DEFAULT 5,
    current_borrow_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 6. 管理员信息表
CREATE TABLE administrators (
    admin_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    contact VARCHAR(20),
    permission_level ENUM('超级管理员', '普通管理员', '图书管理员') DEFAULT '图书管理员',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 7. 借阅记录表
CREATE TABLE borrow_records (
    borrow_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(13),
    student_id VARCHAR(20),
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    renew_count INT DEFAULT 0,
    status ENUM('借出', '已还', '逾期', '遗失') DEFAULT '借出',
    fine_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 8. 图书预约表
CREATE TABLE reservations (
    reservation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(13),
    student_id VARCHAR(20),
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('等待', '可取', '取消', '过期') DEFAULT '等待',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 9. 图书评价表
CREATE TABLE book_reviews (
    review_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(13),
    student_id VARCHAR(20),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 10. 罚款记录表
CREATE TABLE fine_records (
    fine_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR(255),
    payment_status ENUM('未缴纳', '已缴纳', '部分缴纳') DEFAULT '未缴纳',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id)
);

-- 11. 系统日志表
CREATE TABLE system_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    operation_desc TEXT,
    operator_id VARCHAR(20),
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    status ENUM('成功', '失败') DEFAULT '成功',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- 假设操作者可能是系统本身或其他未注册ID，故FK可以为NULL
    FOREIGN KEY (operator_id) REFERENCES administrators(admin_id)
);

-- 12. 通知日志表
CREATE TABLE notification_logs (
    notification_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    notification_type VARCHAR(50) NOT NULL,
    notification_content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- ######################################################################
-- ############################# 索引创建 #############################
-- ######################################################################

-- Books 表索引
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_category ON books(category_code);

-- Borrow_Records 表索引
CREATE INDEX idx_borrow_records_status ON borrow_records(status);

-- Reservations 表索引
CREATE INDEX idx_reservations_status ON reservations(status);

-- Fine_Records 表索引
CREATE INDEX idx_fine_records_status ON fine_records(payment_status);

-- System_Logs 表索引
CREATE INDEX idx_system_logs_operation_time ON system_logs(operation_time);
CREATE INDEX idx_system_logs_operator ON system_logs(operator_id);

-- Notification_Logs 表索引
CREATE INDEX idx_notification_logs_student ON notification_logs(student_id);
CREATE INDEX idx_notification_logs_type ON notification_logs(notification_type);


-- ######################################################################
-- ############################# 触发器 ###############################
-- ######################################################################

DELIMITER //

-- 触发器：更新图书可借数量和学生当前借阅量（借出时）
CREATE TRIGGER after_borrow_insert
AFTER INSERT ON borrow_records
FOR EACH ROW
BEGIN
    UPDATE books
    SET available_copies = available_copies - 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE isbn = NEW.isbn;

    UPDATE students
    SET current_borrow_count = current_borrow_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE student_id = NEW.student_id;
END //

-- 触发器：更新图书可借数量和学生当前借阅量（归还时）
CREATE TRIGGER after_borrow_update_return
AFTER UPDATE ON borrow_records
FOR EACH ROW
BEGIN
    -- 仅在状态从非“已还”变为“已还”时触发
    IF NEW.status = '已还' AND OLD.status != '已还' THEN
        UPDATE books
        SET available_copies = available_copies + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE isbn = NEW.isbn;

        UPDATE students
        SET current_borrow_count = current_borrow_count - 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE student_id = NEW.student_id;
    END IF;
END //

-- 触发器：自动计算逾期罚款
CREATE TRIGGER calculate_fine_on_return
AFTER UPDATE ON borrow_records
FOR EACH ROW
BEGIN
    DECLARE days_overdue INT;
    DECLARE daily_fine DECIMAL(10,2) DEFAULT 1.00; -- 每天罚款金额

    -- 仅在状态从非“已还”变为“已还”时触发
    IF NEW.status = '已还' AND OLD.status != '已还' THEN
        SET days_overdue = DATEDIFF(NEW.return_date, NEW.due_date);

        IF days_overdue > 0 THEN
            INSERT INTO fine_records (
                student_id,
                amount,
                reason,
                payment_status,
                created_date
            ) VALUES (
                NEW.student_id,
                days_overdue * daily_fine,
                CONCAT('图书逾期归还，逾期天数：', days_overdue),
                '未缴纳',
                CURRENT_TIMESTAMP
            );
        END IF;
    END IF;
END //

-- 触发器：更新学生账户状态（当欠款超过阈值时）
CREATE TRIGGER update_student_status_on_fine
AFTER INSERT ON fine_records
FOR EACH ROW
BEGIN
    DECLARE total_unpaid_fine DECIMAL(10,2);
    DECLARE fine_threshold DECIMAL(10,2) DEFAULT 50.00; -- 罚款阈值

    -- 计算该学生未缴纳的罚款总额
    SELECT COALESCE(SUM(amount), 0)
    INTO total_unpaid_fine
    FROM fine_records
    WHERE student_id = NEW.student_id
    AND payment_status != '已缴纳';

    -- 如果未缴纳罚款总额达到阈值，则冻结账户
    IF total_unpaid_fine >= fine_threshold THEN
        UPDATE students
        SET account_status = '冻结',
            updated_at = CURRENT_TIMESTAMP
        WHERE student_id = NEW.student_id;
    END IF;
END //

DELIMITER ;

-- ######################################################################
-- ########################### 存储过程 ###############################
-- ######################################################################

DELIMITER //

-- 存储过程：学期初学生账户初始化
CREATE PROCEDURE initialize_student_accounts(IN semester_name VARCHAR(20))
BEGIN
    -- 重置学生借阅计数和账户状态（不包括已冻结的）
    UPDATE students
    SET current_borrow_count = 0,
        account_status = '正常',
        updated_at = CURRENT_TIMESTAMP
    WHERE account_status != '冻结';

    -- 记录初始化日志
    INSERT INTO system_logs (
        operation_type,
        operation_desc,
        operator_id,
        operation_time
    ) VALUES (
        '账户初始化',
        CONCAT('学期初学生账户初始化完成，学期：', semester_name),
        'SYSTEM', -- 假设系统操作者ID为'SYSTEM'
        CURRENT_TIMESTAMP
    );
END //

-- 存储过程：生成图书流通统计报表
CREATE PROCEDURE generate_circulation_report(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    -- 创建临时表存储统计结果
    DROP TEMPORARY TABLE IF EXISTS temp_circulation_stats;
    CREATE TEMPORARY TABLE temp_circulation_stats (
        category_code VARCHAR(20),
        category_name VARCHAR(100),
        total_borrows INT,
        total_returns INT,
        total_overdue INT,
        total_fines DECIMAL(10,2)
    );

    -- 统计各分类的借阅情况
    INSERT INTO temp_circulation_stats
    SELECT
        bc.category_code,
        bc.category_name,
        COUNT(br.borrow_id) as total_borrows,
        SUM(CASE WHEN br.status = '已还' THEN 1 ELSE 0 END) as total_returns,
        SUM(CASE WHEN br.status = '逾期' THEN 1 ELSE 0 END) as total_overdue,
        COALESCE(SUM(fr.amount), 0) as total_fines
    FROM books b
    JOIN book_categories bc ON b.category_code = bc.category_code
    LEFT JOIN borrow_records br ON b.isbn = br.isbn
    LEFT JOIN fine_records fr ON br.student_id = fr.student_id AND br.borrow_id = (SELECT borrow_id FROM borrow_records WHERE isbn = br.isbn AND student_id = br.student_id AND return_date = fr.created_date ORDER BY created_at DESC LIMIT 1) -- 尝试关联到准确的罚款记录
    WHERE br.borrow_date BETWEEN start_date AND end_date
    GROUP BY bc.category_code, bc.category_name
    ORDER BY total_borrows DESC;

    -- 返回统计结果
    SELECT * FROM temp_circulation_stats;

    -- 清理临时表
    DROP TEMPORARY TABLE IF EXISTS temp_circulation_stats;
END //

-- 存储过程：发送逾期提醒
CREATE PROCEDURE send_overdue_notifications()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_student_id VARCHAR(20);
    DECLARE v_email VARCHAR(100);
    DECLARE v_book_title VARCHAR(255);
    DECLARE v_days_overdue INT;

    -- 声明游标，查找所有“借出”状态且已逾期的记录
    DECLARE cur CURSOR FOR
        SELECT
            br.student_id,
            s.email,
            b.title,
            DATEDIFF(CURRENT_DATE, br.due_date) as days_overdue
        FROM borrow_records br
        JOIN students s ON br.student_id = s.student_id
        JOIN books b ON br.isbn = b.isbn
        WHERE br.status = '借出'
        AND br.due_date < CURRENT_DATE
        -- 避免重复发送：检查 notification_logs 中是否有近期（如1天内）已发送的相同类型通知
        AND NOT EXISTS (
            SELECT 1 FROM notification_logs nl
            WHERE nl.student_id = br.student_id
            AND nl.notification_type = '逾期提醒'
            AND nl.notification_content LIKE CONCAT('%', b.title, '%')
            AND nl.created_at >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)
        );

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- 打开游标
    OPEN cur;

    -- 处理每条逾期记录
    read_loop: LOOP
        FETCH cur INTO v_student_id, v_email, v_book_title, v_days_overdue;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- 插入通知日志
        INSERT INTO notification_logs (
            student_id,
            notification_type,
            notification_content,
            created_at
        ) VALUES (
            v_student_id,
            '逾期提醒',
            CONCAT('您借阅的图书《', v_book_title, '》已逾期', v_days_overdue, '天，请尽快归还。'),
            CURRENT_TIMESTAMP
        );
        -- 实际应用中，这里会调用外部服务发送邮件或短信
    END LOOP;

    -- 关闭游标
    CLOSE cur;
END //

DELIMITER ;

-- ######################################################################
-- ############################## 视图 ################################
-- ######################################################################

-- 当前热门图书视图（借阅量前20，过去3个月）
CREATE VIEW popular_books AS
SELECT
    b.isbn,
    b.title,
    b.author,
    b.publisher,
    bc.category_name,
    COUNT(br.borrow_id) as borrow_count,
    AVG(br.renew_count) as avg_renew_count,
    COUNT(DISTINCT br.student_id) as unique_borrowers
FROM books b
JOIN book_categories bc ON b.category_code = bc.category_code
LEFT JOIN borrow_records br ON b.isbn = br.isbn
WHERE br.borrow_date >= DATE_SUB(CURRENT_DATE, INTERVAL 3 MONTH)
GROUP BY b.isbn, b.title, b.author, b.publisher, bc.category_name
ORDER BY borrow_count DESC
LIMIT 20;

-- 各院系借阅统计视图
CREATE VIEW department_borrow_stats AS
SELECT
    s.department,
    COUNT(DISTINCT s.student_id) as total_students,
    COUNT(br.borrow_id) as total_borrows,
    COUNT(DISTINCT br.isbn) as unique_books_borrowed,
    AVG(br.renew_count) as avg_renew_count,
    SUM(CASE WHEN br.status = '逾期' THEN 1 ELSE 0 END) as overdue_count,
    COALESCE(SUM(fr.amount), 0) as total_fines
FROM students s
LEFT JOIN borrow_records br ON s.student_id = br.student_id
LEFT JOIN fine_records fr ON s.student_id = fr.student_id
GROUP BY s.department;

-- 图书逾期情况视图
CREATE VIEW book_overdue_status AS
SELECT
    b.isbn,
    b.title,
    b.author,
    s.student_id,
    s.name as student_name,
    s.department,
    br.borrow_date,
    br.due_date,
    br.return_date,
    DATEDIFF(CURRENT_DATE, br.due_date) as days_overdue,
    fr.amount as fine_amount,
    fr.payment_status
FROM books b
JOIN borrow_records br ON b.isbn = br.isbn
JOIN students s ON br.student_id = s.student_id
LEFT JOIN fine_records fr ON br.student_id = fr.student_id
WHERE br.status = '逾期' -- 明确标记为逾期
OR (br.status = '借出' AND br.due_date < CURRENT_DATE); -- 仍借出但已过还书日期

-- 图书预约队列视图
CREATE VIEW reservation_queue AS
SELECT
    r.reservation_id,
    b.isbn,
    b.title,
    s.student_id,
    s.name as student_name,
    r.reservation_date,
    r.status,
    ROW_NUMBER() OVER (PARTITION BY b.isbn ORDER BY r.reservation_date) as queue_position
FROM reservations r
JOIN books b ON r.isbn = b.isbn
JOIN students s ON r.student_id = s.student_id
WHERE r.status = '等待'
ORDER BY b.isbn, r.reservation_date;

-- 学生借阅历史视图
CREATE VIEW student_borrow_history AS
SELECT
    s.student_id,
    s.name as student_name,
    s.department,
    b.isbn,
    b.title,
    b.author,
    br.borrow_date,
    br.due_date,
    br.return_date,
    br.status,
    br.renew_count,
    fr.amount as fine_amount,
    fr.payment_status
FROM students s
JOIN borrow_records br ON s.student_id = br.student_id
JOIN books b ON br.isbn = b.isbn
LEFT JOIN fine_records fr ON br.student_id = fr.student_id
ORDER BY s.student_id, br.borrow_date DESC;
