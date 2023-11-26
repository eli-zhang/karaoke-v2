import streamlit as st
from karaoke import find_and_play_song
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
    st.table(df.style.apply(lambda x: ['font-weight: bold' if x.name == st.session_state['current_song_index'] else '' for i in x], axis=1))


# Create a button to start the karaoke
if st.button('Start Karaoke'):
    while st.session_state['current_song_index'] < len(st.session_state['song_queue']):
        st.session_state['current_song_index'] += 1
        find_and_play_song(song)
        # # Get the lyrics
        # lyrics = get_lyrics(song)
        # # Display the lyrics
        # st.write('Lyrics for {}:'.format(song))
        # st.write(lyrics)