import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for Gemini AI
prompt = """
You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing key points within 200 words.
Please provide the summary of the text given here:
"""

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[-1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate summary using Gemini AI
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Custom CSS for styling
st.markdown(
    """
    <style>
        body {
            background-color: #f5f5dc;
        }
        .title {
            color: #800080;
            text-align: center;
            font-size: 36px;
            font-weight: bold;
        }
        .stButton > button {
            background-color: #800080;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: white;
            color: #800080;
            border: 2px solid #800080;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.markdown("<h1 class='title'>YouTube Transcript to Detailed Notes Converter</h1>", unsafe_allow_html=True)

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[-1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    with st.spinner("Extracting transcript..."):
        transcript_text = extract_transcript_details(youtube_link)
    
    if transcript_text.startswith("Error"):
        st.error(transcript_text)
    else:
        with st.spinner("Generating summary..."):
            summary = generate_gemini_content(transcript_text, prompt)
        
        st.markdown("## Detailed Notes:")
        st.write(summary)
