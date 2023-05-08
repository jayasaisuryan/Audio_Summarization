import os
import azure.cognitiveservices.speech as speechsdk
import time
def implement(wavfile):
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

