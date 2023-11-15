import streamlit as st
import sqlite3
from datetime import datetime
import os
from openai import OpenAI

# Retrieve API key from environment variable
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

if openai_api_key is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Function to save the log into SQLite DB
def save_log(prompt, file_path, timestamp):
    conn = sqlite3.connect('tts_log.db')
    c = conn.cursor()
    # Ensure the table is created only once
    c.execute('''CREATE TABLE IF NOT EXISTS logs (prompt TEXT, file_path TEXT, timestamp TEXT)''')
    c.execute('''INSERT INTO logs (prompt, file_path, timestamp) VALUES (?, ?, ?)''', (prompt, file_path, timestamp))
    conn.commit()
    conn.close()

# Function to generate and save audio
def generate_and_save_audio(text, voice, model):
    response = client.audio.speech.create(
        model=model,
        input=input,
        voice=voice,
        response_format="mp3",
        speed=1.0,
    )

    # Generate the audio file path
    file_path = f"generated/audio/{voice}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"

    # generated to dir
    response.stream_to_file(file_path)

    # Ensure the 'audio' directory exists
    os.makedirs('generated/audio', exist_ok=True)
    
    # Log the prompt and file details in the SQLite DB
    save_log(text, file_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return file_path

# Streamlit App
def main():
    st.title('TTS Test App')

    with st.form("tts_form"):
        text = st.text_area("Enter text for TTS:")
        voice = st.selectbox("Choose the voice:", ("alloy", "echo", "fable", "onyx", "nova", "shimmer"))
        model = st.selectbox("Select audio quality:", ("tts-1", "tts-1-hd"))
        stream_audio = st.checkbox("Stream real-time audio")
        submitted = st.form_submit_button("Generate")

        if submitted:
            if stream_audio:
                # Stream and play real-time audio
                st.warning("Streaming audio is not yet implemented in this skeleton.")
            else:
                # Generate and play the audio file
                file_path = generate_and_save_audio(text, voice, model)
                st.audio(file_path)
                st.success(f"Audio file saved at: {file_path}")

    # Page to explore past generations
    if st.button("Explore Past Generations"):
        conn = sqlite3.connect('tts_log.db')
        c = conn.cursor()
        # Query to select all logs and order them by timestamp in descending order
        c.execute('''SELECT * FROM logs ORDER BY timestamp DESC''')
        rows = c.fetchall()
        
        # Close the connection early as we don't need it beyond this point
        conn.close()

        # Create a list of dicts to be displayed in a Streamlit table
        table_data = [{"Prompt": row[0], "Audio": row[1], "Timestamp": row[2]} for row in rows]

        # Display each entry in a nicer format
        for data in table_data:
            st.text(f"Prompt: {data['Prompt']}")
            st.audio(data['Audio'])
            st.text(f"Timestamp: {data['Timestamp']}")



if __name__ == "__main__":
    main()