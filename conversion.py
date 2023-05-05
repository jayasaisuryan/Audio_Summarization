import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import time
import openai
from pydub import AudioSegment
import os
from streamlit_chat import message
import base64

st.set_page_config(page_title="Audio_Summarization")
st.title("Audio Summarization")

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg('Wood.png')

@st.cache_data
def audio_text(wavfile):
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), endpoint='https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken')
    speech_config.speech_recognition_language = "en-US"
    audio_config = speechsdk.audio.AudioConfig(filename=wavfile)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    output_file = open('transcribed.txt', 'w')  # open file in write mode
    done = False
    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True
    def save_transcription(evt):
        nonlocal output_file
        output_file.write(evt.result.text + '\n')
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(save_transcription)  # connect recognized event to save_transcription function
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    speech_recognizer.start_continuous_recognition()
    while not done: 
        time.sleep(.5)
    output_file.close()
    with open('transcribed.txt','r') as copy:
        value = copy.read()
    return value

@st.cache_data
def get_audio(filename):
    input_file = filename
    output_file = "Processed.wav"
    sound = AudioSegment.from_file(input_file)
    sound.export(output_file, format="wav")
    return output_file

@st.cache_data
def generate_response(prompt):
    st.session_state['prompts'].append({"role": "user", "content":prompt})
    completion=openai.ChatCompletion.create(
        engine="Dermatology_AI", # The 'engine' parameter specifies the name of the OpenAI GPT-3.5 Turbo engine to use.
        temperature=0.7, # The 'temperature' parameter controls the randomness of the response.
        max_tokens=2500, # The 'max_tokens' parameter controls the maximum number of tokens in the response.
        top_p=0.95, # The 'top_p' parameter controls the diversity of the response.
        # The 'messages' parameter is set to the 'prompts' list to provide context for the AI model.
        messages = st.session_state['prompts']
    )
    # The response is retrieved from the 'completion.choices' list and appended to the 'generated' list.
    message=completion.choices[0].message.content
    return message

col1,col2 = st.columns(2)
with col1:
    st.header("Initial Step")
    st.subheader("Upload the Audio File")
    input_audio = st.file_uploader("Upload an Audio file :- ",type=['mp3','aac','wav','mpeg'])
    submit = st.button("Submit")
    replica = ""
    if submit:
        if(input_audio.type!="wav"):
            processed_file = get_audio(input_audio)
            subtitles = audio_text(processed_file)
        else:
            processed_file = input_audio
            subtitles = audio_text(processed_file)
        replica += subtitles
    st.download_button("Download transcribed file",replica)

with col2:
    openai.api_type = "azure"
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-03-15-preview"
    if 'prompts' not in st.session_state:
        st.session_state['prompts'] = [{"role": "system", "content": "I'm an AI assistant who's specialised in Call center agent industry. I'll get the trancribed call recording as input and address your doubts regarding it and suggest how to proceed further"}]
    # The 'generated' list stores the AI model's responses to the user's messages.
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    # The 'past' list stores the user's previous messages.
    if 'past' not in st.session_state:
        st.session_state['past'] = []
    def chat_click():
        if st.session_state['user']!= '':
            user_chat_input = st.session_state['user']
            output=generate_response(user_chat_input)
            st.session_state['past'].append(user_chat_input)
            st.session_state['generated'].append(output)
            st.session_state['prompts'].append({"role": "assistant", "content": output})
            st.session_state['user'] = ""
    st.header("QnA Section")
    st.subheader("Text file feeded successfuly")
    st.write(generate_response(replica))
    user_input=st.text_input("Ask Question", key="user")
    chat_button=st.button("Send", on_click=chat_click)
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state['generated'][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

