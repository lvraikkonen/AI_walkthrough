import streamlit as st
from openai import OpenAI
import os, io
from PIL import Image
import base64
from utils.db_utils import init_db, save_tts_log
from utils.db_utils import insert_image, insert_vision_record, get_all_images, get_vision_records
from utils.db_utils import get_tts_records
from datetime import datetime
import pytz
from io import BytesIO
import requests

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
HELICONE_API_KEY = os.getenv("HELICONE_API_KEY")

# Initialize database
init_db()

# Initialize OpenAI Client
client = OpenAI(
    api_key=api_key,
    base_url="http://oai.hconeai.com/v1",  # Set the API endpoint
    default_headers= {
        "Helicone-Auth": f"Bearer {HELICONE_API_KEY}"
    }
)


# Define your local timezone
local_tz = pytz.timezone('Asia/Shanghai')

# Function to convert UTC datetime to local timezone
def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

# Function to generate and save audio
def generate_and_save_audio(text, voice, model):
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3",
            speed=1.0,
        )

    except Exception as error:
        print(str(error))

    # Generate the audio file path
    file_path = f"generated/audio/{voice}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"

    # generated to dir
    response.stream_to_file(file_path)

    # Ensure the 'audio' directory exists
    os.makedirs('generated/audio', exist_ok=True)
    
    # Log the prompt and file details in the SQLite DB
    save_tts_log(text, file_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return file_path


################ GPT4V functions ##################
def encode_image(image):
    """
    Function to encode image to base64, handling PNG with transparency
    """
    buffered = io.BytesIO()
    if image.mode in ("RGBA", "LA"):
        background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
        background.paste(image, image.split()[-1])
        image = background.convert("RGB")
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def ask_openai_vision(base64_image, question):
    """
    Function to make API call to OpenAI
    """
    completion = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages= [
            {
                "role": "system",
                "content": "你是一个得力的AI助手，帮助我识别图片中的内容"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=300,
        # response_format={"type": "json_object"}    
    )
    result = completion.choices[0].message.content
    return result

def generate_image_dalle3(prompt, size, quality):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1
    )
    # Assuming the response object has a 'data' attribute which is a list of Image objects.
    image_data = response.data[0].url  # This should be the correct way to access the URL
    revised_prompt = getattr(response.data[0], 'revised_prompt', 'No revised prompt provided')

    # Convert image URL to binary data and save as PNG
    image_response = requests.get(image_data)
    image = Image.open(BytesIO(image_response.content))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_binary = buffered.getvalue()

    return prompt, revised_prompt, image_binary, image_data, image_response



st.title('OpenAI features')

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["DALL-E 3 Image Generator", "DALL-E 3 Image Gallery", "TTS App", "GPT4Vision App"])

# Page for image generation
if page == "DALL-E 3 Image Generator":
    prompt = st.text_input('Enter the prompt for the image you want to generate:', '')
    size = st.selectbox('Select image size:', ['1024x1024', '1024x1792', '1792x1024'])
    quality = st.selectbox('Select image quality:', ['standard', 'hd'])

    if st.button('Generate Image'):
        if prompt:
            try:
                with st.spinner('DallE-3 is at work...'):
                    prompt, revised_prompt, image_binary, image_data, image_response = generate_image_dalle3(prompt, size, quality)
                image = Image.open(BytesIO(image_response.content))

                insert_image(prompt, revised_prompt, image_binary, image_data)  # Pass the image URL here

                st.image(image, caption='Generated Image', use_column_width=True)
                st.caption(f"Revised prompt: {revised_prompt}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

        else:
            st.warning('Please enter a prompt.')

# Page for image gallery
elif page == "DALL-E 3 Image Gallery":
    st.title("Image Gallery")

    all_images = get_all_images()
    for idx, (id, prompt, revised_prompt, image_binary, image_url, timestamp_str) in enumerate(all_images):
        if image_binary:
            try:
                image = Image.open(BytesIO(image_binary))
                utc_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                local_timestamp = utc_to_local(utc_timestamp)

                st.subheader(f"Prompt: {prompt}")
                st.caption(f"Revised Prompt: {revised_prompt}")
                st.image(image, caption=f"Generated on {local_timestamp.strftime('%Y-%m-%d %H:%M:%S')}", use_column_width=True)
            except Exception as e:
                st.error(f"Could not load image for prompt: '{prompt}'. Error: {e}")
        else:
            st.info(f"No image data available for prompt: '{prompt}'.")

elif page == "TTS App":
    st.title('TTS Test App')

    with st.form("tts_form"):
        text = st.text_area("Enter text for TTS:")
        voice = st.selectbox("Choose the voice:", ("alloy", "echo", "fable", "onyx", "nova", "shimmer"))
        model = st.selectbox("Select audio quality:", ("tts-1", "tts-1-hd"))
        stream_audio = st.checkbox("Stream real-time audio")
        submitted = st.form_submit_button("Generate")

        if submitted:
            with st.spinner('GPT-4 is at work...'):
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
        rows = get_tts_records()

        # Create a list of dicts to be displayed in a Streamlit table
        table_data = [{"Prompt": row[0], "Audio": row[1], "Timestamp": row[2]} for row in rows]

        # Display each entry in a nicer format
        for data in table_data:
            st.text(f"Prompt: {data['Prompt']}")
            st.audio(data['Audio'])
            st.text(f"Timestamp: {data['Timestamp']}")

elif page == "GPT4Vision App":
    st.title('🖼️ GPT-4 Vision Explorer 🔍')

    # Image upload
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        st.write("Image successfully uploaded!")
        base64_image = encode_image(image)

        # Text input for question
        question = st.text_input("What would you like to ask about the image?")

        if st.button('Ask GPT-4 Vision'):
            if question:
                with st.spinner('GPT-4 is at work...'):
                    response = ask_openai_vision(base64_image, question)

                    st.write(response)

                    # Call the insert_record function with base64_image and save the unique path returned
                    unique_image_path = insert_vision_record(question, response, base64_image)

                    # Display the image using the unique path
                    st.image(unique_image_path, caption='Uploaded Image', use_column_width=True)

                    # Optional: Clean up the temp file if needed
                    # os.remove(unique_image_path)
            else:
                st.error('Please enter a question.')

    else:
        st.warning('Please upload an image to get started.')

    # Display the records from the SQLite DB in the Streamlit UI, now with local time
    st.header("Previous Queries")
    records = get_vision_records()
    for record in records:
        # Convert the stored UTC time to local time
        utc_time = datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S')
        local_time = utc_to_local(utc_time).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        st.text(f"Date: {local_time}")
        st.text(f"Prompt: {record[1]}")
        st.text(f"Response: {record[2]}")
        st.text(f"Image Path is: {record[3]}")
        image_path = record[3]
        if os.path.exists(image_path):
            st.image(image_path, caption='Uploaded Image', use_column_width=True)
        else:
            st.error("Image not found.")