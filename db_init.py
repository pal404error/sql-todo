import sqlite3

conn = sqlite3.connect('todo.db')
c = conn.cursor()

# Drop tables if they exist
c.execute('DROP TABLE IF EXISTS users')
c.execute('DROP TABLE IF EXISTS tasks')

# Create users table with proper fields
c.execute('''
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
)
''')

# Create tasks table
c.execute('''
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    due_date TEXT,
    created_by TEXT,
    updated_at TEXT,
    assignee TEXT
)
''')

# Insert default admin user
c.execute('''
INSERT INTO users (id, username, name, email, password, is_admin)
VALUES ('admin-uuid-1', 'admin', 'Admin User', 'admin@example.com', 'admin123', 1)
''')

conn.commit()
conn.close()

print("Database initialized with admin user.")
