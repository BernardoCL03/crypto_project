import streamlit as st
from back.model import SessionLocal, User

# Título para la sección de visualización
st.title('Lista de Usuarios Registrados')

# Crear una sesión para consultar la base de datos
session = SessionLocal()

try:
    # Obtener todos los usuarios
    users = session.query(User).all()
    if users:
        # Mostrar los usuarios en una tabla
        user_data = [[user.id, user.username, user.password_hash, user.user_type] for user in users]
        st.write("Usuarios registrados en el sistema:")
        st.table(user_data)
    else:
        st.write("No hay usuarios registrados.")
except Exception as e:
    st.error("Ocurrió un error al recuperar los usuarios: " + str(e))
finally:
    session.close()