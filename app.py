# Importing necessary libraries
import streamlit as st
from pytube import YouTube
import os
import requests
from zipfile import ZipFile
from time import sleep

# Function to download audio from a YouTube video
def get_youtube_audio(url):
    video = YouTube(url)
    audio = video.streams.get_audio_only()
    audio.download()
    return os.path.join(os.getcwd(), f"{video.title}.mp4")

# Function to upload audio file to AssemblyAI
def upload_audio_to_assemblyai(api_key, filename):
    headers = {'authorization': api_key}
    with open(filename, 'rb') as file:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=file)
    return response.json()['upload_url']

# Function to transcribe audio using AssemblyAI API
def transcribe_audio(api_key, audio_url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    headers = {"authorization": api_key, "content-type": "application/json"}
    data = {"audio_url": audio_url}
    response = requests.post(endpoint, json=data, headers=headers)
    transcript_id = response.json()["id"]
    while True:
        response = requests.get(f"{endpoint}/{transcript_id}", headers=headers)
        if response.json()['status'] == 'completed':
            return response.json()["text"]
        sleep(5)

# Function to save transcription to files
def save_transcription_to_files(text):
    with open('transcription.txt', 'w') as file:
        file.write(text)
    srt_response = requests.get(f"{endpoint}/srt", headers=headers)
    with open("transcription.srt", "w") as file:
        file.write(srt_response.text)
    with ZipFile('transcription.zip', 'w') as file:
        file.write('transcription.txt')
        file.write('transcription.srt')

# Streamlit app
st.markdown('# 📝 **Transcriber App**')
st.warning('Awaiting URL input in the sidebar.')

# Input form
with st.form(key='my_form'):
    url = st.text_input('Enter URL of YouTube video:')
    submit_button = st.form_submit_button(label='Go')

# If form is submitted, execute the app
if submit_button:
    api_key = st.secrets['api_key']
    st.info('Retrieving audio file from YouTube video...')
    audio_file = get_youtube_audio(url)
    st.info('Uploading audio file to AssemblyAI...')
    audio_url = upload_audio_to_assemblyai(api_key, audio_file)
    st.info('Transcribing audio file...')
    text = transcribe_audio(api_key, audio_url)
    st.info('Saving transcription to files...')
    save_transcription_to_files(text)
    with open("transcription.zip", "rb") as zip_download:
        st.download_button(
            label="Download ZIP",
            data=zip_download,
            file_name="transcription.zip",
            mime="application/zip"
        )
