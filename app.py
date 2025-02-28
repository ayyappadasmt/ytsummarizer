import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Missing API Key! Make sure GOOGLE_API_KEY is set in .env")
else:
    genai.configure(api_key=api_key)

# Define the prompt
prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the key points within 250 words.
Please provide the summary of the text given here: """

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[-1].split("&")[0]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        return None

# Function to generate summary using Gemini AI
def generate_gemini_content(transcript_text):
    try:
        model = genai.GenerativeModel("gemini-pro")

        # Limit transcript length to avoid API errors
        max_chars = 3000
        transcript_text = transcript_text[:max_chars]

        response = model.generate_content(prompt + transcript_text)
        return response.text if hasattr(response, 'text') else "Failed to generate summary."
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.markdown('<h1 style="text-align:center; color:#00ff00;">0Labs - YouTube Summarizer</h1>', unsafe_allow_html=True)

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("v=")[-1].split("&")[0]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Get Summary"):
    with st.spinner("🛠️ Extracting transcript..."):
        transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        with st.spinner("🛠️ Generating AI Summary..."):
            summary = generate_gemini_content(transcript_text)

        st.markdown("## Summary:")
        st.write(summary)
    else:
        st.error("Failed to extract transcript. The video may not have subtitles.")
