import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('portal.db')
c = conn.cursor()

# Create Users table (if it doesn't exist)
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)''')

# Create Marks table (if it doesn't exist)
c.execute('''CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    marks INTEGER,
    class TEXT,
    department TEXT
)''')

# Insert 5 users (students, staff, HOD, principal)
users_data = [
    ('student1', 'password1', 'Student'),
    ('student2', 'password2', 'Student'),
    ('staff1', 'password3', 'Staff'),
    ('hod1', 'password4', 'HOD'),
    ('principal', 'password5', 'Principal')
]

c.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users_data)

# Insert 5 sample marks records for students
marks_data = [
    (1, 'CTPS', 85, 'second', 'AIML'),
    (1, 'L1', 90, 'second', 'AIML'),
    (2, 'L1', 78, 'second', 'DS'),
    (2, 'L2', 88, 'second', 'DS'),
    (1, 'L2', 92, 'second', 'AIML'),
]

c.executemany('INSERT INTO marks (student_id, subject, marks, class, department) VALUES (?, ?, ?, ?, ?)', marks_data)

# Commit changes and close the connection
conn.commit()
conn.close()
