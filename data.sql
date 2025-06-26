USE library_system;

-- ######################################################################
-- ############################# 插入示例数据 (修正版) ###################
-- ######################################################################

-- 1. 插入图书分类数据 (book_categories)
INSERT INTO book_categories (category_code, category_name, category_description) VALUES
('CS001', '计算机科学', '涵盖编程、算法、数据结构、网络等'),
('LS002', '文学艺术', '小说、诗歌、戏剧、绘画等'),
('EC003', '经济管理', '经济学、管理学、金融、会计等'),
('HS004', '历史人文', '历史、哲学、社会学等'),
('MD005', '医学健康', '临床医学、公共卫生、营养学等');


-- 2. 插入图书信息数据 (books)
INSERT INTO books (isbn, title, author, publisher, publish_date, price, category_code, location, total_copies, available_copies, status, description, cover_url) VALUES
('9787121264875', 'Python编程从入门到实践', 'Eric Matthes', '机械工业出版社', '2017-06-01', 89.00, 'CS001', 'A区-1层-CS001', 5, 5, '正常', 'Python编程初学者指南', 'http://example.com/python_cover.jpg'),
('9787121401317', 'SQL必知必会', 'Ben Forta', '人民邮电出版社', '2020-03-01', 59.50, 'CS001', 'A区-1层-CS001', 3, 2, '正常', '学习SQL的最佳入门书籍', 'http://example.com/sql_cover.jpg'),
('9787020002202', '活着', '余华', '作家出版社', '1993-01-01', 35.00, 'LS002', 'B区-2层-LS002', 8, 8, '正常', '一部关于中国农民福贵的故事', 'http://example.com/huozhe_cover.jpg'),
('9787508655827', '原则', '瑞·达利欧', '中信出版集团', '2018-01-01', 99.00, 'EC003', 'C区-3层-EC003', 4, 3, '正常', '瑞·达利欧的个人和管理原则', 'http://example.com/yuanze_cover.jpg'),
('9787540484918', '三体', '刘慈欣', '重庆出版社', '2008-01-01', 68.00, 'LS002', 'B区-2层-LS002', 10, 10, '正常', '中国科幻巨作', 'http://example.com/santai_cover.jpg'),
('9787115505051', '深入理解计算机系统', 'Randal E. Bryant', '机械工业出版社', '2018-09-01', 128.00, 'CS001', 'A区-1层-CS001', 2, 1, '正常', '计算机系统经典教材', 'http://example.com/csapp_cover.jpg'),
('9787542661599', '人类简史', '尤瓦尔·赫拉利', '中信出版社', '2014-11-01', 68.00, 'HS004', 'C区-3层-HS004', 6, 6, '正常', '一部探讨人类历史的宏大叙事', 'http://example.com/renleijianshi_cover.jpg');

-- 3. 插入学生信息数据 (students)
INSERT INTO students (student_id, name, gender, department, major, grade, class_name, contact, email, account_status, max_borrow_limit, current_borrow_count) VALUES
('20210001', '张三', '男', '计算机学院', '软件工程', 2021, '软工2101', '13912345678', 'zhangsan@example.com', '正常', 5, 0),
('20210002', '李四', '女', '经济学院', '金融学', 2021, '金融2102', '13887654321', 'lisi@example.com', '正常', 5, 0),
('20220003', '王五', '男', '文学与传媒学院', '汉语言文学', 2022, '汉文2203', '13701234567', 'wangwu@example.com', '正常', 5, 0),
('20200004', '赵六', '男', '医学院', '临床医学', 2020, '临床2004', '13698765432', 'zhaoliu@example.com', '正常', 5, 0);

-- 4. 插入管理员信息数据 (administrators)
INSERT INTO administrators (admin_id, name, position, contact, permission_level) VALUES
('A001', '陈明', '馆长', '18011112222', '超级管理员'),
('A002', '刘芳', '图书管理员', '18933334444', '图书管理员');


-- 5. 插入借阅记录数据 (borrow_records)
-- 假设 P3 借阅事务处理模块已集成触发器来更新 books.available_copies 和 students.current_borrow_count
INSERT INTO borrow_records (isbn, student_id, borrow_date, due_date, status) VALUES
('9787121401317', '20210001', '2023-10-01', '2023-10-31', '借出'), -- 张三借阅SQL必知必会
('9787508655827', '20210002', '2023-09-15', '2023-10-15', '借出'); -- 李四借阅原则

-- 模拟归还 (此条会触发 books.available_copies 和 students.current_borrow_count 更新)
UPDATE borrow_records
SET return_date = '2023-10-25', status = '已还', updated_at = CURRENT_TIMESTAMP
WHERE isbn = '9787121401317' AND student_id = '20210001';

-- 模拟逾期归还 (此条会触发 fine_records 插入)
INSERT INTO borrow_records (isbn, student_id, borrow_date, due_date, status) VALUES
('9787115505051', '20220003', '2023-09-01', '2023-09-30', '借出');
UPDATE borrow_records
SET return_date = '2023-11-05', status = '已还', updated_at = CURRENT_TIMESTAMP
WHERE isbn = '9787115505051' AND student_id = '20220003';

-- 6. 插入图书预约数据 (reservations)
INSERT INTO reservations (isbn, student_id, reservation_date, status) VALUES
('9787540484918', '20210002', '2023-11-10 10:00:00', '等待'),
('9787540484918', '20200004', '2023-11-10 10:05:00', '等待');

-- 7. 插入图书评价数据 (book_reviews)
INSERT INTO book_reviews (isbn, student_id, rating, comment, review_time) VALUES
('9787121401317', '20210001', 5, '非常实用的SQL入门书，讲解清晰易懂！', '2023-10-26 14:30:00'),
('9787115505051', '20220003', 4, '内容很深入，但有些地方对初学者来说略显复杂。', '2023-11-06 10:00:00');

-- 8. 插入罚款记录数据 (fine_records)
-- 注意：这条罚款记录通常由触发器自动生成（例如在 borrow_records 更新时）。
-- 这里为演示目的手动插入，但实际操作中应依赖触发器。
INSERT INTO fine_records (student_id, amount, reason, payment_status, created_date, admin_id) VALUES
('20220003', 6.00, '图书逾期归还，逾期天数：6', '未缴纳', '2023-11-05', 'A002');

-- 9. 插入系统日志数据 (system_logs)
INSERT INTO system_logs (operation_type, operation_desc, operator_id, operation_time, ip_address, status) VALUES
('图书导入', '批量导入50本新书信息', 'A001', '2023-11-01 09:00:00', '192.168.1.100', '成功'),
('学生账户冻结', '学生20220003因欠款超阈值被冻结', NULL, '2023-11-05 08:00:00', 'SERVER_IP', '成功'); -- 修正：'SYSTEM'改为NULL

-- 10. 插入通知日志数据 (notification_logs)
INSERT INTO notification_logs (student_id, notification_type, notification_content, is_read) VALUES
('20220003', '逾期提醒', '您借阅的图书《深入理解计算机系统》已逾期6天，请尽快归还。', FALSE),
('20210002', '预约可取', '您预约的图书《三体》已有副本可借阅，请前往图书馆办理。', FALSE);