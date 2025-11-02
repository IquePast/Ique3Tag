from shazamio import Shazam

import asyncio

async def recognize_song(file_path):
    shazam = Shazam()
    out = await shazam.recognize(file_path)
    return out['track']['title'], out['track']['subtitle']

# Exemple d'utilisation
song_info = asyncio.run(recognize_song(r'C:\Users\Martin\Desktop\Musique\2008\11_Novembre\Lorie - Play (mixwill rmx).mp3'))
print(song_info)
