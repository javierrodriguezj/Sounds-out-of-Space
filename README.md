# Sounds out of Space.

## ℹ️ Overview

Sounds out of Space (SooS) is **currently being developed**. SooS is a bot that will post a video (everyday at 12.00h (CET) on [Valencian physics student local section's account](https://x.com/EstRSEF_UV)) of the galactic object which Hubble photographed each day of the year. The video will contain a *song* that describes Hubble's picture.

This project was born in NASA's Hackathon (NASA Space Apps Challenge) to face the challenge called: *'Symphony of the Stars: Harmonizing the James Webb Space Telescope in Music and Images'*. Our team was formed by physics students which belong to the Valencian physics students local section. We wanted to divulgate our effort done during the hackathon through and X bot.

We are using Github actions in order to automate the process.


## 🌟 Highlights

- The picture we are using are taken from [here](https://science.nasa.gov/mission/hubble/multimedia/what-did-hubble-see-on-your-birthday/).
- The main script consists of three parts.
  1. Take the picture of the current day.
  2. Transform the picture to an audio and build the video with that audio.
  3. Post the tweet with a general description of the galactic object.


## 🚀 Algorithm
To transform our desired picture into something that resembles a song:
1. Get the RGB code for each picture's pixel and take the median by columns.
2. We established that we will be working with: 5 notes duration (Red values), 15 different frequencies following a pentatonic scale (Green values) and 11 types of volumes (Blue values).
3. Create for each note duration and frequency a sinusoidal function that will be concatenated with the following ones.

The volume changes linearly from the last volume to the current one.


## 💭 Feedback 
Feel free to contact us throught our [X account]((https://x.com/EstRSEF_UV))
