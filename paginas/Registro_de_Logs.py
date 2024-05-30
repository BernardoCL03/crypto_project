import streamlit as st
import pandas as pd
from back.model import SessionLocal, Logs

#st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def ver_logs():

    # Título para la sección de visualización
    st.title('Logs Registrados')

    # Crear una sesión para consultar la base de datos
    session = SessionLocal()

    if st.session_state.get('authenticated'):
            if st.session_state['user_type'] == 'Admin':
                try:
                    # Obtener todos los usuarios
                    logs = session.query(Logs).all()
                    if logs:
                        # Preparar los datos para la tabla
                        log_info = [[log.id, log.user_name, log.user_type, log.action, log.description, log.timestamp] for log in logs]
                        # Crear un DataFrame con pandas y especificar los nombres de las columnas
                        df = pd.DataFrame(log_info, columns=['Log_ID', 'Username', 'Privilegios', 'Acción', "Descripción", "Timestamp"])
                        st.success("Logs registrados en el sistema:")
                        st.table(df)
                    else:
                        st.write("No existen logs registrados.")
                except Exception as e:
                    st.error("Ocurrió un error al recuperar los usuarios: " + str(e))
                finally:
                    session.close()

    # En teoria esto jamas se ve (ya que en menu.py se establece un filtro)
    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')