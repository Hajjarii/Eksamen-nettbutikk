from flask import Flask, render_template
import mariadb
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route('/')
def hjem():
    try:
        with mariadb.connect(
        user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port=3306,
            database=os.getenv("DB_NAME")) as conn:

            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM produkter")
            produkter = mycursor.fetchall()

            return render_template('index.html', produkter=produkter)

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return "Kunne ikke koble til databasen", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
