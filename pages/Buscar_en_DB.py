import os
import streamlit as st
import base64
import pyotp
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from back.encrypt import decrypt_data
from sqlalchemy.orm import joinedload
import pandas as pd
# our decrypt data function
from back.encrypt import decrypt_data, decrypt_large_data, admin_decrypt_page

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

if st.session_state.get('authenticated'):
    st.sidebar.write(f"Usuario: {st.session_state['username']}")
    st.sidebar.write(f"Permisos: {st.session_state['user_type']}")
    if st.sidebar.button("Cerrar sesión"):
        # Al hacer clic en cerrar sesión, cambiamos el estado a no autenticado
        st.session_state.authenticated = False


# Iniciamos la página
if __name__ == "__main__":
    st.title(':exclamation: Admin Decryption :exclamation:')

    if st.session_state.get('authenticated') and st.session_state['user_type'] == 'Admin':

        if 'otp_verified' not in st. session_state:
            st.session_state['otp_verified'] = False
        
        if not st.session_state['otp_verified']:

            st.markdown("""
                #### Bienvenido a la sección de administración. Esta página está diseñada exclusivamente para el acceso y la gestión por parte de administradores autorizados.

                ## Información Sensible

                Es importante destacar que esta área contiene información sensible sobre migrantes. Debido a la naturaleza delicada de los datos, se implementan medidas estrictas de seguridad y encriptación para proteger esta información.

                ### Acceso Restringido

                **Solo los administradores tienen acceso a esta página.** Si usted está aquí, es porque ha sido verificado y autorizado para manejar dichos datos. Le pedimos proceder con la máxima precaución y responsabilidad.

                ### Responsabilidad

                Como administrador, tiene la responsabilidad de:
                - **Proteger la confidencialidad y la integridad de la información.**
                - **Asegurar que el acceso a los datos se realice de forma segura y solo cuando sea estrictamente necesario.**

                Agradezemos su compromiso con la seguridad y el respeto por la privacidad de los individuos cuyos datos están a nuestro cuidado.
            """)

            st.warning("Ingrese la OTP para acceder a esta página")
            opt_input = st.text_input("OTP", type = "password")

            dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
            load_dotenv(dotenv_path=dotenv_path)
            TOTP_SECRET = os.getenv("TOTP_SECRET")

            totp = pyotp.TOTP(TOTP_SECRET)
            if st.button("Verificar OTP"):
                if totp.verify(opt_input):
                    st.session_state['otp_verified'] = True
                    st.success("OTP verificada correctamente")
                    st.rerun()
                else:
                    st.error("OTP incorrecta, favor de intentar de nuevo")

        if st.session_state['otp_verified']:

            dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
            load_dotenv(dotenv_path=dotenv_path)
            TOTP_SECRET = os.getenv("TOTP_SECRET")

            # leemos en formato base64, tenemos que convertirla a objeto valido
            private_key_base64 = os.getenv('PRIVATE_KEY')
            private_key_pem = base64.b64decode(private_key_base64)
            PRIVATE_KEY = load_pem_private_key(private_key_pem, password=TOTP_SECRET.encode())
            data = admin_decrypt_page(PRIVATE_KEY)
            
            df = pd.json_normalize(data, sep='_')
            # Extraer la lista de nombres
            # Crear una columna 'full_name' combinando 'name' y 'last_name'
            df['full_name'] = df['name'] + ' ' + df['last_name']
            df = df[['full_name'] + [col for col in df.columns if col != 'full_name']]
            df.drop(['name','last_name'], axis = 1, inplace=True)
            # Agregar un menú para seleccionar el formato de búsqueda
            if 'consult' not in st.session_state:
                search_type = st.selectbox('Seleccione el método de búsqueda', ['Seleccione', 'Nombre completo', 'Fecha de registro'])
                selected_migrant = None
                selected_id = None

                if search_type == 'Nombre completo':
                    all_names = df['full_name'].unique()
                    selected_migrant = st.selectbox('Seleccione un nombre', ['Seleccione'] + list(all_names))
                    if selected_migrant != 'Seleccione':
                        ids_for_name = df[df['full_name'] == selected_migrant]['id'].unique()
                        if len(ids_for_name) > 1:
                            st.write(f"Parece que hay múltiples registros bajo el nombre {selected_migrant}")
                            selected_id = st.selectbox('Seleccione el ID', ['Seleccione'] + list(ids_for_name))
                        else:
                            selected_id = ids_for_name[0]


                elif search_type == 'Fecha de registro':
                    unique_dates = df['arrival_date'].unique()
                    selected_date = st.selectbox('Seleccione una fecha', ['Seleccione'] + list(unique_dates))
                    if selected_date != 'Seleccione':
                        filtered_df = df[df['arrival_date'] == selected_date]
                        selected_name = st.selectbox('Seleccione un nombre', ['Seleccione'] + filtered_df['full_name'].tolist())
                        if selected_name != 'Seleccione':
                            selected_id = filtered_df[filtered_df['full_name'] == selected_name]['id'].values[0]
                            selected_migrant = selected_name

                if selected_migrant and selected_id and st.button('Consultar información', key='consultar_info'):
                    st.session_state['selected_migrant'] = selected_migrant
                    st.session_state['selected_id'] = selected_id
                    st.session_state['consult'] = True
                    st.experimental_rerun()

            if st.session_state.get('consult'):
                selected_id = st.session_state['selected_id']
                selected_migrant = st.session_state['selected_migrant']
                st.write(f'Consulta de información sobre {selected_migrant}')
                df_migrant = df[(df['full_name'] == selected_migrant) & (df['id'] == selected_id)]
                st.image(base64.b64decode(df_migrant['front_photo'].values[0]), caption='Foto de frente')
                data_type = st.selectbox('Seleccione el tipo de dato', ['Seleccione', 'General', 'Health', 'Transit', 'Education'])

                if data_type != 'Seleccione':
                    if data_type == 'General':
                        columnas = [col for col in df_migrant.columns if not any(prefix in col for prefix in ['transit', 'health', 'education'])]
                        columnas.remove('full_name')
                        columnas.remove('front_photo')
                        columnas.remove('right_profile_photo')
                        columnas.remove('left_profile_photo')
                    elif data_type == 'Health':
                        columnas = [col for col in df_migrant.columns if 'health' in col]
                    elif data_type == 'Transit':
                        columnas = [col for col in df_migrant.columns if 'transit' in col]
                    elif data_type == 'Education':
                        columnas = [col for col in df_migrant.columns if 'education' in col]

                    df_seleccionado = df_migrant[columnas]
                    df_transpuesto = df_seleccionado.transpose()
                    df_transpuesto.columns = [selected_migrant]
                    st.dataframe(df_transpuesto, width=1200, height=600)

                    st.image(base64.b64decode(df_migrant['right_profile_photo'].values[0]), caption='Foto de perfil derecho')
                    st.image(base64.b64decode(df_migrant['left_profile_photo'].values[0]), caption='Foto de perfil izquierdo')

                if st.button('Finalizar consulta', key='finalizar_consulta'):
                    del st.session_state['selected_migrant']
                    del st.session_state['selected_id']
                    del st.session_state['consult']
                    st.experimental_rerun()

    
    elif st.session_state.get('authenticated') and st.session_state['user_type'] == 'User':
        st.error('No tienes permisos para acceder a esta página.')
    
    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')
        