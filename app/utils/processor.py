from youtube_transcript_api import YouTubeTranscriptApi
import io
import pdfplumber

def extract_youtube_text(video_url: str):
    """Extracts transcript from a YouTube URL."""
    video_id = video_url.split("v=")[-1].split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t['text'] for t in transcript])

def extract_pdf_text(content):
    """Extracts text from an uploaded PDF file."""
    file_ptr = io.BytesIO(content)

    text = ""
    with pdfplumber.open(file_ptr) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def extract_text():
    return None