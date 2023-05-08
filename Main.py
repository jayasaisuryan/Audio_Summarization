import os
import wav_convert as WC
import text_convert as TC
import pandas as pd
import tiktoken
import openai

openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-03-15-preview"

#number = int(input("Enter the number of files : "))
if not os.path.exists("Text Files/"):
    os.mkdir("Text Files/")

    for audio_file in os.listdir("Audio Files/"):
        if audio_file.endswith("wav"):
            path = "Audio Files/"+audio_file
            text_file = TC.implement(path)
            text_filename = os.path.splitext(audio_file)[0]
            with open("Text Files/"+text_filename+".txt","w") as wr:
                wr.write(text_file)
        
        else:
            path = "Audio Files/"+audio_file
            wav_file = WC.get_audio(path)
            text_file = TC.implement(wav_file)
            text_filename = os.path.splitext(audio_file)[0]
            with open("Text Files/"+text_filename+".txt","w") as wr:
                wr.write(text_file)

else:
    os.mkdir("Embeddings")
    df = pd.DataFrame(columns = ['fname', 'text'])
    fname = []
    text = []
    for textfiles in os.listdir("Text Files/"):
        fname.append(os.path.splitext(textfiles)[0])
        with open("Text Files/"+textfiles,'r') as txt:
            content = txt.read()
            content.replace('\n',' ')
            text.append(content)
    df['fname'] = fname
    df['text'] = text
    df.to_csv("Embeddings/Tabular.csv")
    tokenizer = tiktoken.get_encoding("cl100k_base")
    df1 = pd.read_csv("Embeddings/Tabular.csv", index_col=0)
    df1['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    df1.to_csv("Embeddings/Tokenized.csv")
    df2 = pd.read_csv("Embeddings/Tokenized.csv",index_col=0)
    df2['embeddings'] = df2.text.apply(lambda x: openai.Embedding.create(input=x, engine='Embedding_Task')['data'][0]['embedding'])
    df2.to_csv('Embeddings/Embeddings.csv')



