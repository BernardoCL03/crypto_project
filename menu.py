
import os
from dotenv import load_dotenv
#import pickle
#from pathlib import Path
import streamlit as st
import yaml

import streamlit_authenticator as stauth
from  yaml.loader import SafeLoader

load_dotenv()

st.set_page_config(
    page_title='Casa Monarca',
    page_icon=':butterfly:',
)

# ---- User Authentication ----
file_path = os.path.join(os.path.dirname(__file__), 'credentials.yaml')

# read credentials from .yaml file
with open(file_path, 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

# cookies so that the user doesn't have to re-authenticate, a cookie password and when do credentials expire
authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'],
                                    config['cookie']['key'], config['cookie']['expiry_days'],
                                    config['preauthorized'])

st.markdown("""
        # Casa Monarca :butterfly:
            
        ### Somos una organización que acoge, protege, promueve e integra a los migrantes. Aqui echar más rollo y todo ese show, o depende más de qué es lo que ellos busquen.
        """)

name, authentication_status, username = authenticator.login('Inicio de sesión', 'main')


if authentication_status is True:

    st.write('# Bienvenido 👋 a la página web de la base de datos de Casa Monarca :butterfly:.')

    # --- Side Bar ---
    authenticator.logout('Cerrar sesión', 'sidebar')
    if 'casa_monarca_auth' in st.session_state:
        authenticator.logout("Cerrar sesión", "sidebar")

    st.markdown(
        """
        Holaaaaa, esto es unicamente de prueba, estoy viendo que showwww. Hola, chingue su madre esto
    """)

elif authentication_status is False:
    st.error('El usuario y/o la contraseña son incorrectos.')

elif authentication_status is None:
    st.warning("Por favor introduce tu usuario y contraseña.")
