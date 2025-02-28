import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load API Key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the prompt
prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the key points within 250 words.
Please provide the summary of the text given here: """

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        return str(e)

# Function to generate summary using Gemini AI
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit UI
st.markdown(
    """
    <style>
    body {
        background-color: black;
        color: #00ff00;
        font-family: 'Courier New', monospace;
    }
    .stTextInput > div > div > input {
        background-color: black;
        color: #00ff00;
        border: 2px solid #00ff00;
    }
    .stButton > button {
        background-color: #00ff00;
        color: black;
        font-size: 16px;
        padding: 10px;
        transition: 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background-color: black;
        color: #00ff00;
        border: 2px solid #00ff00;
    }
    .title {
        font-size: 40px;
        text-align: center;
        text-shadow: 0 0 10px #00ff00;
        animation: glow 1.5s infinite alternate;
    }
    @keyframes glow {
        from {
            text-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00;
        }
        to {
            text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">0Labs - YouTube Summarizer</h1>', unsafe_allow_html=True)

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button(" Get Summary"):
    with st.spinner("🛠️ Extracting transcript..."):
        transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        with st.spinner(" Generating AI Summary..."):
            summary = generate_gemini_content(transcript_text, prompt)

        st.markdown("## Summary:")
        st.write(summary)
