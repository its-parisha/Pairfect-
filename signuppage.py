
from flask import Flask, request, jsonify, session
import pymysql
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # Use environment variable for security

# Database configuration (set via environment variables for better security)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'digital_twin_db')

def get_db_connection():
    """Establish and return a database connection."""
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor  # Return results as dictionaries
        )
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def home():
    """Protected home route for logged-in users."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in.'}), 401
    return jsonify({
        'message': f'Welcome to your digital twin dashboard, {session["username"]}!',
        'user_id': session['user_id']
    })

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not all([username, email, password]):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
            (username, email, password_hash)
        )
        conn.commit()
        return jsonify({'message': 'Signup successful! You can now log in.'}), 201
    except pymysql.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 409
    except pymysql.Error as e:
        print(f"Signup error: {e}")
        return jsonify({'error': 'An error occurred during signup'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not all([username, password]):
        return jsonify({'error': 'Username and password are required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT id, username, password_hash FROM users WHERE username = %s',
            (username,)
        )
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({
                'message': 'Login successful',
                'user': {'id': user['id'], 'username': user['username']}
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except pymysql.Error as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'An error occurred during login'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
