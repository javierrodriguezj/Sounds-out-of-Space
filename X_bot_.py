import pandas as pd
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO
import numpy as np
import soundfile as sf
from moviepy.editor import ImageClip, AudioFileClip
import tempfile
import os
import tweepy
from dotenv import load_dotenv


def rgb_rows(imagen):
    imagen = imagen.convert('RGB')

    # size of the image
    width, height = imagen.size

    R = []
    G = []
    B = []


    for y in range(height):
        r_values = []
        g_values = []
        b_values = []

        for x in range(width):
            rgb = imagen.getpixel((x, y))

            #RGB values
            r_values.append(rgb[0])
            g_values.append(rgb[1])
            b_values.append(rgb[2])

        median_r = int(np.median(r_values)) % 5
        median_g = int(np.median(g_values)) % 15
        median_b = int(np.median(b_values)) % 11

        R.append(median_r)
        G.append(median_g)
        B.append(median_b)

    # Median values
    return R, G, B


def duration(R):  # R rhythm vector
    dur_notas = [2**(-elemento) for elemento in R] #time in seconds for each frequency
    tiempo_total = np.sum(dur_notas)
    return dur_notas, tiempo_total


def frecuencia(G, frecuencias):
    nota = [frecuencias[modulo] for modulo in G] #identify each G-value to its frequency
    return nota

def volumen(B):
    B = np.array(B)
    aux = np.ones(len(B))
    v = 0.2*aux + 0.08*B
    return v

# Generate the wave
def generate_wave(frequency, duration, sample_rate, vi, vj, fase=0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=True)
    aux = np.ones(len(t))
    alfa = vi*aux + (vj-vi)*t
    wave = np.sin(2 * np.pi * frequency * t + fase) * alfa
    fasew = 2 * np.pi * frequency * duration + fase #we need to concatenate properly the phase of the wave
    return wave, fasew



def imagen_audio(entrada):
    sample_rate = 44100  # Frequency sampling
    frecuencias = [261.626, 293.663, 329.628, 391.995, 440, 523.251, 587.33, 659.255,
                   783.991, 880, 1046.5, 1174.66, 1318.55, 1567.98, 195.998, 220]
    
    # RGB
    R, G, B = rgb_rows(entrada)
    
    #General parametres (rhythm, frequencies, volumes)
    dur_notas, _ = duration(R)
    frecuencias_G = frecuencia(G, frecuencias)
    v=volumen(B)

    #Create our signal
    audio_signal = np.array([])
    
    #First wave (previous phase=0)
    wave, fase = generate_wave(frecuencias_G[0], dur_notas[0], sample_rate, v[0],v[1])
    
    # Concatenate waves 
    for idx, (freq, dur) in enumerate(zip(frecuencias_G[1:], dur_notas[1:])):
        audio_signal = np.concatenate((audio_signal, wave))
        wave, fase = generate_wave(freq, dur, sample_rate,v[idx],v[(idx+1)], fase)
    
    #Last wave
    audio_signal = np.concatenate((audio_signal, wave))


    # Normalising
    audio_signal = audio_signal / np.max(np.abs(audio_signal))

    return  audio_signal, sf.write('audio.wav', audio_signal, sample_rate)
    

#Create the video
def create_video(image_file, audio_signal, output_path, sample_rate=44100):

    image_array = np.array(image_file)

    #Temporal file for the audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        sf.write(temp_audio_path, audio_signal, sample_rate)

    try:
        image_clip = ImageClip(image_array)#Picture for the background

        audio_clip = AudioFileClip(temp_audio_path) #create a clip audio

        image_clip = image_clip.set_duration(audio_clip.duration)#set duration

       
        video = image_clip.set_audio(audio_clip)#combine picture+audio


        #save localy
        video_buffer = BytesIO()
        video.write_videofile(video_buffer, fps=24, codec="libx264", audio_codec="aac")
        video_buffer.seek(0) 
    

        return video_buffer
    finally:
        #Delete temporal files
        os.remove(temp_audio_path)


def publicar_tweet(api, video_buffer, tweet_text): #Post tweet

    # Truncate if text is larger than tweet and add ...
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..." 


    media = api.media_upload(filename="video.mp4", file=video_buffer)
    api.update_status(status=tweet_text, media_ids=[media.media_id])


if __name__ == "__main__":

    clean_data=pd.read_excel('clean_data.xlsx')
    current_date=datetime.now()
    month=current_date.strftime('%B').lower()
    day=int(current_date.strftime('%-d').lower())

    clean_date=clean_data[(clean_data['Day']==day)& (clean_data['Month']==month)]

    if not clean_date.empty:
        for _, row in clean_date.iterrows():
            object_name = row['Obj']
            caption = row['Caption']  
            image_url = f"https://imagine.gsfc.nasa.gov/hst_bday/images/{month}-{day}-2019-{object_name}.jpg"


    image_response=requests.get(image_url) #make request to get image
    if image_response.status_code == 200:
        image = Image.open(BytesIO(image_response.content))

    image_response = requests.get(image_url)


    if image_response.status_code == 200: #image saved succesfully
            image = Image.open(BytesIO(image_response.content))
            audio, _ = imagen_audio(image)


            video_buffer = create_video(image, audio)

            #X authentification
            load_dotenv()
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
            api = tweepy.API(auth)

            # post tweet
            tweet_text=f'La foto del día '
            publicar_tweet(api, video_buffer, tweet_text)






        