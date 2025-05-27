from flask import Flask, request, jsonify, render_template, g
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Kết nối cơ sở dữ liệu SQLite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('exam_types.db')
        db.row_factory = sqlite3.Row
        # Tạo bảng nếu chưa tồn tại
        db.execute('''CREATE TABLE IF NOT EXISTS exam_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            priority INTEGER NOT NULL,
            last_modified_by TEXT,
            last_modified_date TEXT
        )''')
        db.commit()
    return db

# Đóng kết nối khi ứng dụng kết thúc
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Route hiển thị trang chính
@app.route('/')
def index():
    return render_template('index.html')

# Lấy danh sách Hình thức thi (hỗ trợ sắp xếp)
@app.route('/get_exam_types', methods=['GET'])
def get_exam_types():
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    valid_sorts = ['name', 'title', 'priority', 'last_modified_date']
    if sort not in valid_sorts:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'asc'
    db = get_db()
    cursor = db.execute(f"SELECT * FROM exam_types ORDER BY {sort} {order}")
    rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows])

# Thêm mới Hình thức thi
@app.route('/add_exam_type', methods=['POST'])
def add_exam_type():
    name = request.form['name']
    title = request.form['title']
    priority = request.form['priority']
    last_modified_by = 'admin'  # Giả định người dùng là admin
    last_modified_date = datetime.now().strftime('%d/%m/%y %H:%M')
    db = get_db()
    cursor = db.execute(
        "INSERT INTO exam_types (name, title, priority, last_modified_by, last_modified_date) VALUES (?, ?, ?, ?, ?)",
        (name, title, priority, last_modified_by, last_modified_date)
    )
    db.commit()
    new_id = cursor.lastrowid
    new_entry = {
        'id': new_id,
        'name': name,
        'title': title,
        'priority': priority,
        'last_modified_by': last_modified_by,
        'last_modified_date': last_modified_date
    }
    return jsonify(new_entry)

# Cập nhật Hình thức thi
@app.route('/update_exam_type', methods=['POST'])
def update_exam_type():
    id = request.form['id']
    name = request.form['name']
    title = request.form['title']
    priority = request.form['priority']
    last_modified_by = 'admin'
    last_modified_date = datetime.now().strftime('%d/%m/%y %H:%M')
    db = get_db()
    db.execute(
        "UPDATE exam_types SET name=?, title=?, priority=?, last_modified_by=?, last_modified_date=? WHERE id=?",
        (name, title, priority, last_modified_by, last_modified_date, id)
    )
    db.commit()
    updated_entry = {
        'id': id,
        'name': name,
        'title': title,
        'priority': priority,
        'last_modified_by': last_modified_by,
        'last_modified_date': last_modified_date
    }
    return jsonify(updated_entry)

# Xóa Hình thức thi
@app.route('/delete_exam_type', methods=['POST'])
def delete_exam_type():
    id = request.form['id']
    db = get_db()
    db.execute("DELETE FROM exam_types WHERE id=?", (id,))
    db.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)