import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from PIL import Image
import requests
import os

st.set_page_config(
    page_title="Talk to your pics!",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)
# Path: Main.py
# Adopted by: Ali Nazem
#------------------------------------------------------------
#HEADER
st.markdown('''
Powered by Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
, Streamlit and Python''', unsafe_allow_html=True)
st.caption("By Ali Nazem. For educational purposes ONLY")

#------------------------------------------------------------
#LANGUAGE
langcols = st.columns([0.2,0.8])
with langcols[0]:
  lang = st.selectbox('Select your language',
  ('English', 'Español', 'Français', 'Deutsch',
  'Italiano', 'Português', 'Polski', 'Nederlands',
  'Русский', '日本語', '한국어', '中文', 'العربية',
  'हिन्दी', 'Türkçe', 'Tiếng Việt', 'Bahasa Indonesia',
  'ภาษาไทย', 'Română', 'Ελληνικά', 'Magyar', 'Čeština',
  'Svenska', 'Norsk', 'Suomi', 'Dansk', 'हिन्दी', 'हिन्�'),index=1)

if 'lang' not in st.session_state:
    st.session_state.lang = lang
st.divider()

#------------------------------------------------------------
#FUNCTIONS

@st.cache_resource
def load_model() -> genai.GenerativeModel:
    """
    The function `load_model()` returns an instance of the `genai.GenerativeModel` class initialized with the model name
    'gemini-pro'.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro')
    return model



#------------------------------------------------------------
#CONFIGURATION
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


model = load_model()


if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat()

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

#st.session_state.chat_session

#------------------------------------------------------------
#CHAT

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state or lang != st.session_state.lang:
    st.session_state.lang = lang
    welcome  = model.generate_content(f'''
    Give a brief friendly welcome greeting to the user and suggest what they can do (You can describe images, answer questions, read text files, and read tables). Your name is Pubby Healthy. Introduce your self. generate the answer in {lang}''')
    welcome.resolve()
    st.session_state.welcome = welcome

    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)
else:
    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)


cols=st.columns(3)

with cols[0]:
    if lang == 'Español':
      image_atachment = st.toggle("Adjuntar imagen", value=False, help="Activa este modo para adjuntar una imagen y que el chatbot pueda leerla")
    else:
      image_atachment = st.toggle("Attach image", value=False, help="Activate this mode to attach an image and let the chatbot read it")

with cols[1]:
    if lang == 'Español':
      txt_atachment = st.toggle("Adjuntar archivo de texto", value=False, help="Activa este modo para adjuntar un archivo de texto y que el chatbot pueda leerlo")
    else:
      txt_atachment = st.toggle("Attach text file", value=False, help="Activate this mode to attach a text file and let the chatbot read it")
with cols[2]:
    if lang == 'Español':
      csv_excel_atachment = st.toggle("Adjuntar CSV o Excel", value=False, help="Activa este modo para adjuntar un archivo CSV o Excel y que el chatbot pueda leerlo")
    else:
      csv_excel_atachment = st.toggle("Attach CSV or Excel", value=False, help="Activate this mode to attach a CSV or Excel file and let the chatbot read it")

        
if image_attachment:
    if lang == 'Español':
        image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
        url = st.text_input("O pega la url de tu imagen")
    else:
        image = st.file_uploader("Upload your image", type=['png', 'jpg', 'jpeg'])
        url = st.text_input("Or paste your image URL")
else:
    image = None
    url = ''


if txt_atachment:
    if lang == 'Español':
      txtattachment = st.file_uploader("Sube tu archivo de texto", type=['txt'])
    else:
      txtattachment = st.file_uploader("Upload your text file", type=['txt'])
else:
    txtattachment = None

if csv_excel_atachment:
    if lang == 'Español':
      csvexcelattachment = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])
    else:
      csvexcelattachment = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])
else:
    csvexcelattachment = None
if lang == 'Español':
  prompt = st.chat_input("Escribe tu mensaje")
else:
  prompt = st.chat_input("What's on your mind?")

if prompt:
    txt = ''
    if txtattachment:
        txt = txtattachment.getvalue().decode("utf-8")
        if lang == 'Español':
          txt = '   Archivo de texto: \n' + txt
        else:
          txt = '   Text file: \n' + txt

    if csvexcelattachment:
        try:
            df = pd.read_csv(csvexcelattachment)
        except:
            df = pd.read_excel(csvexcelattachment)
        txt += '   Dataframe: \n' + str(df)


    if len(txt) > 5000:
        txt = txt[:5000] + '...'
    if image or url != '':
        if url != '':
            img = Image.open(requests.get(url, stream=True).raw)
        else:
            img = Image.open(image)
        prmt  = [prompt + txt, img]
    else:
        prmt  = [prompt + txt]


    if lang == 'Español':
      spinertxt = 'Espera un momento, estoy pensando...'
    else:
      spinertxt = 'I am thinking. Be right with you ...'
    with st.spinner(spinertxt):
            try:
                if len(prmt) > 1:
                    response = st.session_state.chat.send_message(prmt)
                    response.resolve()
                else:
                    response = st.session_state.chat.send_message(prmt[0])
            except Exception as e:
                    st.session_state.chat.send_message(f'{type(e).__name__}: {e}')
            st.rerun()







