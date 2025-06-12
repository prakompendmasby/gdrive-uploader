from flask import Flask, request, render_template, redirect, url_for
import os
import datetime
import psycopg2
from werkzeug.utils import secure_filename
from drive_uploader import upload_to_drive

app = Flask(__name__)

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS")
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    gdrive_url TEXT,
    uploaded_at TIMESTAMP
)
''')
conn.commit()

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(filename)

            # Upload to Google Drive
            gdrive_url = upload_to_drive(filename)

            # Insert record into PostgreSQL
            now = datetime.datetime.now()
            cursor.execute("INSERT INTO uploads (filename, gdrive_url, uploaded_at) VALUES (%s, %s, %s)",
                           (filename, gdrive_url, now))
            conn.commit()

            os.remove(filename)
            return redirect(url_for('upload'))

    cursor.execute("SELECT filename, gdrive_url, uploaded_at FROM uploads ORDER BY uploaded_at DESC")
    files = cursor.fetchall()
    return render_template('upload.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
