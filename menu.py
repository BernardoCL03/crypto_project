import streamlit as st
from back.model import SessionLocal, User
import bcrypt
import time

# Importar las funciones de las páginas
from paginas.Buscar_en_DB import buscar_en_db_page
from paginas.Creacion_de_Usuarios import creacion_de_usuarios_page
from paginas.Registro_de_Migrantes import registro_migrantes_page
from paginas.Ver_Usuarios import ver_usuarios_page
from paginas.Visualizar_datos import visualizar_datos_page
from paginas.Registro_de_Logs import ver_logs

# Configuración de la página (debe ser la primera llamada de Streamlit)
st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')


def menu_principal(username, user_type):
    if user_type == 'Admin':
        
        st.markdown(f"""
            # ¡Bienvenido {username}, al Sistema de Gestión de Migrantes de casa Monarca :butterfly:! 

            Este portal web está diseñado para facilitar la administración y visualización de información de migrantes. Proporciona herramientas tanto para usuarios administradores como para usuarios normales, cada uno con niveles de acceso y capacidades distintas dentro del sistema.

            ## Páginas y Funcionalidades

            ### 1. **Registro de Migrantes**
            - **Descripción**: Esta pestaña permite la captura de información detallada de los migrantes.

            ### 2. **Buscar en DB**
            - **Descripción**: Permite realizar consultas específicas dentro de la base de datos para acceder a la información registrada de los migrantes.

            ### 3. **Creación de Usuarios**
            - **Descripción**: Esta sección está reservada para los administradores, quienes pueden crear nuevos usuarios asignando credenciales de acceso como administrador o usuario normal.

            ### 4. **Manejo de Usuarios**
            - **Descripción**: Permite a los administradores visualizar una lista de todos los usuarios, así como manejar los niveles acceso de estos.
                
            ### 5. **Visualizar datos**
            - **Descripción**: Permite a usuarios y administradores la posibilidad de ver gráficas interactivas y atractivas.

            ### 6. **Registro de logs**
            - **Descripción**: Permite a administradores consultar registros de migrantes añadidos, dados de baja y cuando se realizan búsquedas en la base de datos.

            ## Nota Importante
            Este sistema maneja información sensible. Es crucial mantener la confidencialidad y la seguridad de los datos en todo momento. Cada usuario debe adherirse a las normas de seguridad establecidas para garantizar la protección de la información.
        """)
        
    elif user_type == 'User':
        st.markdown(f"""
            # ¡Bienvenido {username}, al Sistema de Gestión de Migrantes de casa Monarca :butterfly:! 

            Este portal web está diseñado para facilitar la administración y visualización de información de migrantes. Proporciona herramientas para usuarios normales con el objetivo de capturar y visualizar información de manera eficiente y segura.

            ## Páginas y Funcionalidades

            ### 1. **Registro de Migrantes**
            - **Descripción**: Esta pestaña permite la captura de información detallada de los migrantes.

            ### 2. **Visualizar datos**
            - **Descripción**: Permite a usuarios y administradores la posibilidad de ver gráficas interactivas y atractivas.

            ### 3. **Buscar en DB**
            - **Descripción**: Permite realizar consultas específicas dentro de la base de datos para acceder a la información registrada de los migrantes.

            ## Nota Importante
            Este sistema maneja información sensible. Es crucial mantener la confidencialidad y la seguridad de los datos en todo momento. Cada usuario debe adherirse a las normas de seguridad establecidas para garantizar la protección de la información.
        """)
    elif user_type == 'Colaborador':
        st.markdown(f"""
            # ¡Bienvenido {username}, al Sistema de Gestión de Migrantes de casa Monarca :butterfly:! 

            Este portal web está diseñado para facilitar la administración y visualización de información de migrantes. Proporciona herramientas para usuarios normales con el objetivo de capturar y visualizar información de manera eficiente y segura.

            ## Páginas y Funcionalidades

            ### 1. **Registro de Migrantes**
            - **Descripción**: Esta pestaña permite la captura de información detallada de los migrantes.

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
    # Navegación entre páginas
    if st.session_state['user_type'] == "Admin":
        page =  st.sidebar.selectbox("Seleccionar página", ["Menú", "Registro de Migrantes","Visualizar datos","Buscar en DB","Creación de Usuarios","Manejo de Usuarios", "Ver Registro Logs"])
    elif st.session_state['user_type'] == 'User':
        page =  st.sidebar.selectbox("Seleccionar página", ["Menú", "Registro de Migrantes","Visualizar datos", 'Buscar en DB'])
    elif st.session_state['user_type'] == 'Colaborador':
        page =  st.sidebar.selectbox("Seleccionar página", ["Menú", "Registro de Migrantes"])


    # Manejo de la barra lateral y la sesión
if st.session_state.get('authenticated'):
    st.sidebar.write(f"Usuario: {st.session_state['username']}")
    st.sidebar.write(f"Permisos: {st.session_state['user_type']}")
    if st.sidebar.button("Cerrar sesión"):
        # Al hacer clic en cerrar sesión, cambiamos el estado a no autenticado
        st.session_state.authenticated = False
        st.session_state.otp_verified = False
        st.rerun()

    # Mostrar la página seleccionada
    if page == "Buscar en DB":
        buscar_en_db_page()
    elif page == "Creación de Usuarios":
        creacion_de_usuarios_page()
    elif page == "Registro de Migrantes":
        registro_migrantes_page()
    elif page == "Manejo de Usuarios":
        ver_usuarios_page()
    elif page == "Visualizar datos":
        visualizar_datos_page()
    elif page == 'Ver Registro Logs':
        ver_logs()
    elif page == "Menú":
        menu_principal(st.session_state['username'], st.session_state['user_type'])
