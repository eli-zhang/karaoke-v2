print("Run `python -m pip install -U git+https://github.com/facebookresearch/demucs` if you get package issues.")
print("You may also need to run `brew install ffmpeg` as well on mac.")
print("Also run pip install -r requirements.txt")

import io
from pathlib import Path
import select
from shutil import rmtree
import subprocess as sp
import sys
import yt_dlp
import json
import re
import requests
import urllib.request 
from bs4 import BeautifulSoup 
from typing import Dict, Tuple, Optional, IO
from youtubesearchpython import SearchVideos
from playsound import playsound

# Customize the following options!
model = "htdemucs"
extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.
two_stems = "vocals"   # only separate one stems from the rest, for instance

# Options for the output audio.
mp3 = True
mp3_rate = 320
float32 = False  # output as float 32 wavs, unsused if 'mp3' is True.
int24 = False    # output as int24 wavs, unused if 'mp3' is True.
# You cannot set both `float32 = True` and `int24 = True` !!

# https://www.quora.com/Whats-a-good-API-to-use-to-get-song-lyrics
def get_lyrics(song_title): 
    # remove all except alphanumeric characters from artist and song_title 
    title = re.sub(' ', "+", song_title)
    search_url = 'https://search.azlyrics.com/search.php?q={}'.format(title)
    print(search_url)
    page = requests.get(search_url)
    try:
        soup = BeautifulSoup(page.content, 'html.parser')
        url = soup.find('td').find('a')['href']

    except Exception as e: 
        return "Exception occurred \n" + str(e) 
     
    try: 
        content = urllib.request.urlopen(url).read() 
        soup = BeautifulSoup(content, 'html.parser') 
        lyrics = str(soup) 
        # lyrics lies between up_partition and down_partition 
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->' 
        down_partition = '<!-- MxM banner -->' 
        lyrics = lyrics.split(up_partition)[1] 
        lyrics = lyrics.split(down_partition)[0] 
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('<br/>','').replace('</div>','').replace('<i>','').replace('</i>','').strip() 
        return lyrics 
    except Exception as e: 
        return "Exception occurred \n" +str(e) 

def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()

def separate(input_path=None, output_path=None):
    cmd = ["python3", "-m", "demucs.separate", "-o", output_path, "-n", model]
    if mp3:
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
    if float32:
        cmd += ["--float32"]
    if int24:
        cmd += ["--int24"]
    if two_stems is not None:
        cmd += [f"--two-stems={two_stems}"]

    print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + input_path, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")

while True:
    print('enter a song: ')
    name = input()
    print('searching...')
    search = SearchVideos(name, offset = 1, mode = "json", max_results = 1)
    result = json.loads(search.result())['search_result'][0]
    link = result['link']
    init_title = result['title']
    title = "".join([c for c in init_title if c.isalpha() or c.isdigit()]).rstrip()
    artist = result['channel']
    print('loading...')

    ydl_opts = {
        'outtmpl': './downloaded_songs/{}.%(ext)s'.format(title),
        'format': 'bestaudio/best',
        'keepvideo': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([link])

    print("done downloading.")

    separate(["downloaded_songs/{}.mp3".format(title)], "processed_songs")

    playsound('processed_songs/{}/{}/no_vocals.mp3'.format(model, title), block=False)
    print(get_lyrics(name))