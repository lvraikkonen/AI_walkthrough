import sqlite3
import os, uuid
from PIL import Image
import base64

def init_db():
    """
    Initialize SQLite DB
    """
    conn = sqlite3.connect('MyOpenAI_App.db')
    # init table for vision use
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vision_queries
                 (date TEXT, prompt TEXT, response TEXT, image_path TEXT)''')
    
    conn.commit()
    conn.close()
    
    # init table for generate image use
    conn = sqlite3.connect('MyOpenAI_App.db')
    # init table for vision use
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS generated_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                image_binary BLOB,
                image_url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                revised_prompt TEXT
            );
        ''')
    try:
        c.execute('ALTER TABLE generated_images ADD COLUMN image_url TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists, ignore
    
    conn.commit()
    conn.close()

    # init table for tts gen logs
    conn = sqlite3.connect('MyOpenAI_App.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tts_logs (prompt TEXT, file_path TEXT, timestamp TEXT)''')

    conn.commit()
    conn.close()


def insert_image(prompt, revised_prompt, image_binary, image_url):
    """
    insert_image function to accept and store binary image data
    """
    with sqlite3.connect('MyOpenAI_App.db') as conn:
        conn.execute('INSERT INTO generated_images (prompt, revised_prompt, image_binary, image_url) VALUES (?, ?, ?, ?)', 
                     (prompt, revised_prompt, image_binary, image_url))


def get_all_images():
    """
    Function to get all image records
    """
    with sqlite3.connect('MyOpenAI_App.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, prompt, revised_prompt, image_binary, image_url, timestamp FROM generated_images ORDER BY timestamp DESC')
        return cur.fetchall()

# Function to save the log into SQLite DB
def save_tts_log(prompt, file_path, timestamp):
    conn = sqlite3.connect('MyOpenAI_App.db')
    c = conn.cursor()
    # Ensure the table is created only once
    c.execute('''CREATE TABLE IF NOT EXISTS tts_logs (prompt TEXT, file_path TEXT, timestamp TEXT)''')
    c.execute('''INSERT INTO tts_logs (prompt, file_path, timestamp) VALUES (?, ?, ?)''', (prompt, file_path, timestamp))
    conn.commit()
    conn.close()

def get_tts_records():
    conn = sqlite3.connect('MyOpenAI_App.db')
    c = conn.cursor()
    # Query to select all logs and order them by timestamp in descending order
    c.execute('''SELECT * FROM tts_logs ORDER BY timestamp DESC''')
    rows = c.fetchall()
       
    # Close the connection early as we don't need it beyond this point
    conn.close()

    return rows

# Modify the insert_record function to save files with unique names and write bytes
def insert_vision_record(prompt, response, base64_image):
    conn = sqlite3.connect('MyOpenAI_App.db')
    c = conn.cursor()
    unique_filename = f'uploaded/image_{uuid.uuid4()}.jpeg'
    image_data = base64.b64decode(base64_image)
    with open(unique_filename, 'wb') as f:
        f.write(image_data)
    c.execute("INSERT INTO vision_queries VALUES (datetime('now'), ?, ?, ?)",
              (prompt, response, unique_filename))
    conn.commit()
    conn.close()
    return unique_filename

# Function to get records from the SQLite DB
def get_vision_records():
    conn = sqlite3.connect('MyOpenAI_App.db')
    c = conn.cursor()
    c.execute("SELECT date, prompt, response, image_path FROM vision_queries ORDER BY date DESC")
    records = c.fetchall()
    conn.close()
    return records