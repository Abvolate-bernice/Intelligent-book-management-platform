// 主要的JavaScript功能

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function () {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 自动隐藏警告消息
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // 表格排序功能
    initTableSorting();
});

// 表格排序功能
function initTableSorting() {
    var tables = document.querySelectorAll('.table-sortable');
    tables.forEach(function (table) {
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function (header) {
            header.addEventListener('click', function () {
                var column = this.getAttribute('data-sort');
                var direction = this.getAttribute('data-direction') === 'asc' ? 'desc' : 'asc';

                // 清除其他列的排序状态
                headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));

                // 设置当前列的排序状态
                this.classList.add(direction === 'asc' ? 'sort-asc' : 'sort-desc');
                this.setAttribute('data-direction', direction);

                // 执行排序
                sortTable(table, column, direction);
            });
        });
    });
}

// 表格排序实现
function sortTable(table, column, direction) {
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort(function (a, b) {
        var aValue = a.querySelector('td[data-' + column + ']').getAttribute('data-' + column);
        var bValue = b.querySelector('td[data-' + column + ']').getAttribute('data-' + column);

        if (direction === 'asc') {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });

    // 重新插入排序后的行
    rows.forEach(function (row) {
        tbody.appendChild(row);
    });
}

// AJAX请求工具函数
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (successCallback) successCallback(response);
                } catch (e) {
                    if (errorCallback) errorCallback('响应解析失败');
                }
            } else {
                if (errorCallback) errorCallback('请求失败: ' + xhr.status);
            }
        }
    };

    xhr.onerror = function () {
        if (errorCallback) errorCallback('网络错误');
    };

    if (data) {
        xhr.send(JSON.stringify(data));
    } else {
        xhr.send();
    }
}

// 显示消息提示
function showMessage(message, type) {
    var alertClass = 'alert-' + (type || 'info');
    var alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    var container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);

        // 自动隐藏
        setTimeout(function () {
            var alert = container.querySelector('.alert');
            if (alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        if (callback) callback();
    }
}

// 格式化日期
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 格式化时间
function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 数字格式化
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 表单验证
function validateForm(form) {
    var isValid = true;
    var inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

    inputs.forEach(function (input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// 清除表单
function clearForm(form) {
    var inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(function (input) {
        input.value = '';
        input.classList.remove('is-invalid', 'is-valid');
    });
}

// 搜索功能
function performSearch(searchTerm, searchUrl) {
    if (searchTerm.trim()) {
        window.location.href = searchUrl + '?search=' + encodeURIComponent(searchTerm);
    }
}

// 分页功能
function goToPage(page) {
    var currentUrl = new URL(window.location);
    currentUrl.searchParams.set('page', page);
    window.location.href = currentUrl.toString();
}

// 导出功能
function exportData(format, data) {
    var blob;
    var filename = 'export_' + new Date().toISOString().slice(0, 10) + '.' + format;

    if (format === 'csv') {
        blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
    } else if (format === 'json') {
        blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    }

    if (blob) {
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }
}

// 图表初始化（如果使用Chart.js）
function initCharts() {
    // 这里可以初始化各种图表
    console.log('Charts initialized');
}

// 响应式表格处理
function handleResponsiveTable() {
    var tables = document.querySelectorAll('.table-responsive');
    tables.forEach(function (table) {
        if (table.scrollWidth > table.clientWidth) {
            table.classList.add('has-scroll');
        }
    });
}

// 键盘快捷键
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        // Ctrl/Cmd + S: 保存
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            // 触发保存操作
        }

        // Ctrl/Cmd + F: 搜索
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            var searchInput = document.querySelector('#search');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
}

// 初始化所有功能
function initAll() {
    initTableSorting();
    handleResponsiveTable();
    initKeyboardShortcuts();
    initCharts();
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
} else {
    initAll();
}

// ====== 动态科技极简风点阵连线背景 ======
(function () {
    const canvas = document.getElementById('tech-bg');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = window.innerWidth;
    let height = window.innerHeight;
    let dpr = window.devicePixelRatio || 1;
    let points = [];
    const POINT_NUM = Math.floor((width * height) / 6000); // 点的数量随屏幕自适应
    const LINE_DIST = 140; // 连线最大距离
    const MOVE_SPEED = 0.3;

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);
    }

    function randomPoint() {
        return {
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * MOVE_SPEED,
            vy: (Math.random() - 0.5) * MOVE_SPEED
        };
    }

    function initPoints() {
        points = [];
        for (let i = 0; i < POINT_NUM; i++) {
            points.push(randomPoint());
        }
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);
        // 画点
        ctx.fillStyle = 'rgba(0, 180, 255, 0.8)';
        points.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
            ctx.fill();
        });
        // 画线
        for (let i = 0; i < points.length; i++) {
            for (let j = i + 1; j < points.length; j++) {
                const p1 = points[i], p2 = points[j];
                const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                if (dist < LINE_DIST) {
                    ctx.strokeStyle = `rgba(0,180,255,${1 - dist / LINE_DIST})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
    }

    function update() {
        points.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;
        });
    }

    function animate() {
        update();
        draw();
        requestAnimationFrame(animate);
    }

    function reset() {
        resize();
        initPoints();
    }

    window.addEventListener('resize', reset);
    reset();
    animate();
})();
// ====== 动态背景代码结束 ====== 