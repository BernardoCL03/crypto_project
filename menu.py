import streamlit as st
from back.model import SessionLocal, User
import bcrypt
import time

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def menu_principal(username):
    st.markdown("""
            # Bienvenido al Sistema de Gestión de Migrantes de casa Monarca :butterfly:

            Este portal web está diseñado para facilitar la administración y visualización de información de migrantes. Proporciona herramientas tanto para usuarios administradores como para usuarios normales, cada uno con niveles de acceso y capacidades distintas dentro del sistema.

            ## Páginas y Funcionalidades

            ### 1. **Registro de Migrantes**
            - **Descripción**: Esta pestaña permite la captura de información detallada de los migrantes.
            - **Acceso**: Usuarios y administradores.

            ### 2. **Buscar en DB**
            - **Descripción**: Funcionalidad exclusiva para administradores que permite realizar consultas específicas dentro de la base de datos para acceder a la información registrada de los migrantes.
            - **Acceso**: Solo administradores.

            ### 3. **Creación de Usuarios**
            - **Descripción**: Esta sección está reservada para los administradores, quienes pueden crear nuevos usuarios asignando credenciales de acceso como administrador o usuario normal.
            - **Acceso**: Solo administradores.

            ### 4. **Ver Usuarios**
            - **Descripción**: Permite a los administradores visualizar una lista de todos los usuarios registrados en el sistema, mostrando detalles como el nombre de usuario y el tipo de acceso que poseen.
            - **Acceso**: Solo administradores.

            ## Nota Importante
            Este sistema maneja información sensible. Es crucial mantener la confidencialidad y la seguridad de los datos en todo momento. Cada usuario debe adherirse a las normas de seguridad establecidas para garantizar la protección de la información.
            """)

# Inicializamos las variables de sesión si no existen
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Función de inicio de sesión
def login():
    st.title('Iniciar Sesión')
    username = st.text_input("Nombre de usuario", key="login_username")
    password = st.text_input("Contraseña", type="password", key="login_password")
    submit_button = st.button("Iniciar sesión")

    if submit_button:
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                password_entered = password.encode('utf-8')
                password_stored = user.password_hash.encode('utf-8') if isinstance(user.password_hash, str) else user.password_hash
                if bcrypt.checkpw(password_entered, password_stored):
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.session_state['id'] = user.id
                    st.session_state['user_type'] = user.user_type
                    st.success(f"Has iniciado sesión exitosamente {st.session_state['username']}")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error('Nombre de usuario o contraseña incorrectos.')
            else:
                st.error("Nombre de usuario o contraseña incorrectos.")
        except Exception as e:
            st.error("Ocurrió un error al intentar iniciar sesión: " + str(e))
        finally:
            session.close()

# Comprobamos si el usuario está autenticado
if not st.session_state['authenticated']:
    login()
else:
    menu_principal(st.session_state['username'])
