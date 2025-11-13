from flask import Flask
import mysql.connector, time

app = Flask(__name__)

@app.route('/')
def home():
    for i in range(5): 
        try:
            conn = mysql.connector.connect(
                host='db',
                user='root',
                password='root',
                database='studentdb'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 'Hello from MySQL inside Docker!'")
            result = cursor.fetchone()
            conn.close()
            return f"<h2>{result[0]}</h2>"
        except Exception as e:
            print(f"MySQL not ready yet... retrying ({i+1}/5)")
            time.sleep(5)
    return "❌ Could not connect to MySQL"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
