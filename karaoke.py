print("Run `pip install -r requirements.txt` to install dependencies.")
print("You may also need to run `brew install ffmpeg` as well on mac.")

from helpers import find_and_play_song

while True:
    print('enter a song: ')
    query_name = input()

    find_and_play_song(query_name)

    
