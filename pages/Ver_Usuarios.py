import streamlit as st
import pandas as pd
from back.model import SessionLocal, User

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

if st.session_state.get('authenticated'):
    st.sidebar.write(f"Usuario: {st.session_state['username']}")
    st.sidebar.write(f"Permisos: {st.session_state['user_type']}")
    if st.sidebar.button("Cerrar sesión"):
        # Al hacer clic en cerrar sesión, cambiamos el estado a no autenticado
        st.session_state.authenticated = False

# Título para la sección de visualización
st.title('Usuarios Registrados')

# Crear una sesión para consultar la base de datos
session = SessionLocal()

if st.session_state.get('authenticated'):
    if st.session_state['user_type'] == 'Admin':
        try:
            # Obtener todos los usuarios
            users = session.query(User).all()
            if users:
                # Preparar los datos para la tabla
                user_data = [[user.id, user.username, user.user_type] for user in users]
                # Crear un DataFrame con pandas y especificar los nombres de las columnas
                df = pd.DataFrame(user_data, columns=['user_id', 'username', 'user_type'])
                st.success("Usuarios registrados en el sistema:")
                st.table(df)
            else:
                st.write("No hay usuarios registrados.")
        except Exception as e:
            st.error("Ocurrió un error al recuperar los usuarios: " + str(e))
        finally:
            session.close()
    
    elif st.session_state['user_type'] == 'Colaborador' or st.session_state['user_type'] == 'User':
        st.error(f"¡Lo sentimos {st.session_state['username']}! Solamente usuarios con permisos de Admin tienen derecho a utilizar esta página.")
else:
    st.error('Favor de iniciar sesión para acceder a esta página.')