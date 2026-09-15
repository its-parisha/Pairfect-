from flask import Flask, request, jsonify, session
import pymysql
import bcrypt
import os
import requests  # For AI API integration (optional)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'digital_twin_db')

def get_db_connection():
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        return None

# Existing routes (signup, login, logout, home) remain unchanged...

@app.route('/add_company_data', methods=['POST'])
def add_company_data():
    """Allow logged-in users to add company data."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    data_type = data.get('data_type')
    data_value = data.get('data_value')
    
    if not all([data_type, data_value]):
        return jsonify({'error': 'data_type and data_value required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO company_data (user_id, data_type, data_value) VALUES (%s, %s, %s)',
            (session['user_id'], data_type, data_value)
        )
        conn.commit()
        return jsonify({'message': 'Company data added successfully'}), 201
    except pymysql.Error as e:
        print(f"Add data error: {e}")
        return jsonify({'error': 'Failed to add data'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/chat', methods=['POST'])
def chat():
    """Chatbot endpoint: Responds based on user queries about company data and trends."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    message = data.get('message', '').lower().strip()
    
    if not message:
        return jsonify({'response': 'Please ask a question!'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    response = "I'm sorry, I didn't understand that. Try asking about 'data' or 'trends'."
    
    try:
        if 'data' in message:
            # Fetch user's company data
            cursor.execute('SELECT data_type, data_value FROM company_data WHERE user_id = %s', (session['user_id'],))
            user_data = cursor.fetchall()
            if user_data:
                response = f"Your company data: {', '.join([f'{d['data_type']}: {d['data_value']}' for d in user_data])}"
            else:
                response = "No company data found. Add some via /add_company_data."
        
        elif 'trend' in message:
            # Fetch AI trends (simulate AI analysis or call external API)
            cursor.execute('SELECT trend_name, analysis FROM trends ORDER BY generated_at DESC LIMIT 5')
            trends = cursor.fetchall()
            if trends:
                response = "Latest AI-analyzed trends: " + "; ".join([f"{t['trend_name']}: {t['analysis']}" for t in trends])
            else:
                response = "No trends available yet."
        
        # Optional: Integrate real AI (e.g., OpenAI)
        # Uncomment and set API_KEY in environment
        # if 'ai' in message:
        #     ai_response = requests.post('https://api.openai.com/v1/chat/completions', 
        #                                 headers={'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}'},
        #                                 json={'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': message}]})
        #     if ai_response.status_code == 200:
        #         response = ai_response.json()['choices'][0]['message']['content']
    
    except pymysql.Error as e:
        print(f"Chat error: {e}")
        response = "An error occurred while processing your query."
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({'response': response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
