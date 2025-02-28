import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ Missing API Key! Make sure GOOGLE_API_KEY is set in .env")
else:
    genai.configure(api_key=api_key)

# Define the prompt
prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the key points within 250 words.
Please provide the summary of the text given here: """

# Function to extract transcript (supports multiple languages)
def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID (supports both `watch?v=` and `youtu.be/`)
        if "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[-1].split("?")[0]
        elif "watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[-1].split("&")[0]
        else:
            return None, "Invalid YouTube URL format."

        # Try fetching English transcript
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en']).fetch()
        except NoTranscriptFound:
            # Try fetching any available transcript
            transcript = transcript_list.find_generated_transcript(['en']).fetch()
        
        # Combine transcript text
        transcript_text = " ".join([i["text"] for i in transcript])
        return transcript_text, None
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return None, "No subtitles available for this video in English."
    except VideoUnavailable:
        return None, "This video is unavailable or private."
    except Exception as e:
        return None, f"Error fetching transcript: {str(e)}"

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
        transcript_text, error_message = extract_transcript_details(youtube_link)

    if transcript_text:
        with st.spinner("🛠️ Generating AI Summary..."):
            summary = generate_gemini_content(transcript_text)

        st.markdown("## Summary:")
        st.write(summary)
    else:
        st.error(f"❌ {error_message}")
