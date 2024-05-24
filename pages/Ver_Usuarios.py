import streamlit as st
import pandas as pd
from back.model import SessionLocal, User

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
else:
    st.error('Favor de iniciar sesión para acceder a esta página.')