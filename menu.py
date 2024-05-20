
import streamlit as st
from pages.input_page import input_page
from pages.dataframe_page import dataframe_page
from pages.pie_chart_page import pie_chart_page
from back.model import SessionLocal, User
import bcrypt


st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

# # Sidebar navigation
# page = st.sidebar.selectbox("Choose a page", ['Input Page', 'Dataframe Visualization', 'Pie Chart'])

# if page == 'Input Page':
#     input_page()
# elif page == 'Dataframe Visualization':
#     dataframe_page()
# elif page == 'Pie Chart':
#     pie_chart_page()


st.title('Iniciar Sesión')

username = st.text_input("Nombre de usuario", key="login_username")
password = st.text_input("Contraseña", type="password", key="login_password")

if st.button('Iniciar Sesión'):
    session = SessionLocal()
    try:
        # filtramos al usuario correspondiente con username
        user = session.query(User).filter(User.username == username).first()
        if user:
            # tenemos que asegurarnos de que el password ingresado (password) y el password dentro de la tabla (user.password_hash) sean bytes
            password_entered = password.encode('utf-8')
            password_stored = user.password_hash.encode('utf-8') if isinstance(user.password_hash, str) else user.password_hash
            
            # checamos que ambos hashes sean iguales
            if bcrypt.checkpw(password_entered, password_stored):
                st.session_state['authenticated'] = True
                st.session_state['user_type'] = user.user_type
                st.session_state['username'] = username
                st.success("Has iniciado sesión exitosamente!")
            else:
                st.error('Nombre de usuario o contraseña incorrectos.')
        else:
            st.error("Nombre de usuario o contraseña incorrectos.")
    except Exception as e:
        st.error("Ocurrió un error al intentar iniciar sesión: " + str(e))
    finally:
        session.close()