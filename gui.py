print("To run this GUI, run `streamlit run gui.py`.")

import streamlit as st
from helpers import find_song
import pandas as pd

if 'song_queue' not in st.session_state:
    st.session_state['song_queue'] = []
if 'current_song_index' not in st.session_state:
    st.session_state['current_song_index'] = -1

with st.form(key='song_form'):
    # Create a text input for the song request inside the form
    song_request = st.text_input('Enter a song:')
    # Create a submit button for the form
    submit_button = st.form_submit_button(label='Add to queue')

# Check if the form is submitted
if submit_button:
    st.session_state['song_queue'].append(song_request)
    st.success(f'Song "{song_request}" added to queue!')

# Display the song queue
st.write('Song Queue:')
if st.session_state['song_queue']:
    df = pd.DataFrame(st.session_state['song_queue'], columns=['Songs'])
    df['Songs'] = df['Songs'].apply(lambda x: f"> {x}" if df[df['Songs'] == x].index[0] == st.session_state['current_song_index'] else x)
    df['Remove'] = range(len(df))
    df = df.set_index('Remove')
    st.table(df.style.apply(lambda x: ['font-weight: bold' if x.name == st.session_state['current_song_index'] else '' for i in x], axis=1))

    # Add a button for each song in the queue to remove it
    for i in range(len(st.session_state['song_queue'])):
        if st.button(f'Remove song {i}'):
            st.session_state['song_queue'].pop(i)
            st.session_state['current_song_index'] = -1 if i == st.session_state['current_song_index'] else st.session_state['current_song_index'] - 1 if i < st.session_state['current_song_index'] else st.session_state['current_song_index']
            st.experimental_rerun()


# Create a button to start the karaoke
if st.button('Start Karaoke'):
    while st.session_state['current_song_index'] < len(st.session_state['song_queue']) - 1:
        st.session_state['current_song_index'] += 1
        st.experimental_rerun()
        song = st.session_state['song_queue'][st.session_state['current_song_index']]
        path_to_song = find_song(song)

        st.audio(path_to_song, format="audio/mp3", start_time=0)
        # # Get the lyrics
        # lyrics = get_lyrics(song)
        # # Display the lyrics
        # st.write('Lyrics for {}:'.format(song))
        # st.write(lyrics)