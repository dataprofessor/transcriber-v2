# Importing necessary libraries
import streamlit as st
from pytube import YouTube
import os
import requests
from zipfile import ZipFile
from time import sleep

# Initialize session state
if 'endpoint' not in st.session_state:
    st.session_state['endpoint'] = 'https://api.assemblyai.com/v2/transcript'
if 'transcript_id' not in st.session_state:
    st.session_state['transcript_id'] = ''
if 'headers' not in st.session_state:
    st.session_state['headers'] = {"authorization": st.secrets['api_key'], "content-type": "application/json"}
                                                                     
# Function to download audio from a YouTube video
def get_youtube_audio(url):
    video = YouTube(url)
    audio = video.streams.get_audio_only()
    return audio.download()

# Function to upload audio file to AssemblyAI
def upload_audio_to_assemblyai(filename):
    headers = {'authorization': st.secrets['api_key']}
    with open(filename, 'rb') as file:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=file)
    return response.json()['upload_url']

# Function to transcribe audio using AssemblyAI API
def transcribe_audio(audio_url):
    data = {"audio_url": audio_url}
    response = requests.post(st.session_state['endpoint'], json=data, headers=st.session_state['headers'])
    st.session_state['transcript_id'] = response.json()["id"]
    while True:
        response = requests.get(f"{st.session_state['endpoint']}/{st.session_state['transcript_id']}", headers=st.session_state['headers'])
        if response.json()['status'] == 'completed':
            return response.json()["text"]
        sleep(3)

# Function to save transcription to files
def save_transcription_to_files(text):
    with open('transcription.txt', 'w') as file:
        file.write(text)
    srt_response = requests.get(f"{st.session_state['endpoint']}/{st.session_state['transcript_id']}/srt", headers={"authorization": st.secrets['api_key']})
    with open("transcription.srt", "w") as file:
        file.write(srt_response.text)
    with ZipFile('transcription.zip', 'w') as file:
        file.write('transcription.txt')
        file.write('transcription.srt')

        
st.title('Transcriber App')

# Input form
with st.form(key='my_form'):
    url = st.text_input('Enter URL of YouTube video:')
    submit_button = st.form_submit_button(label='Go')

# If form is submitted, execute the app
if submit_button:
    with st.spinner('Calculating ...'):
        placeholder = st.empty()
        placeholder.info('Retrieving audio file from YouTube video...')
        audio_file = get_youtube_audio(url)
        placeholder.info('Uploading audio file to AssemblyAI...')
        audio_url = upload_audio_to_assemblyai(audio_file)
        placeholder.info('Transcribing audio file...')
        text = transcribe_audio(audio_url)
        placeholder.info('Saving transcription to files...')
        save_transcription_to_files(text)
        placeholder.info('Calculation complete!', icon='ℹ️')
        with open("transcription.zip", "rb") as zip_download:
            st.download_button(
                label="Download ZIP",
                data=zip_download,
                file_name="transcription.zip",
                mime="application/zip"
            )
