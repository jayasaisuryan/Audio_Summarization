from pydub import AudioSegment
  
def get_audio(filename):
    output_file = 'converted.wav'
    sound = AudioSegment.from_file(filename)
    sound.export(output_file, format="wav")
    return output_file