import os
import streamlit as st
import base64
import pyotp
import time
#from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import pandas as pd
import datetime
from datetime import datetime
# our decrypt data function
from back.model import SessionLocal, General, Logs # table names
from back.encrypt import admin_decrypt_page, encrypt_data, encrypt_large_data

#st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def buscar_en_db_page():

    st.title(':exclamation: Admin Decryption :exclamation:')

    if st.session_state.get('authenticated'): 
    
        if st.session_state['user_type'] == 'Admin' or st.session_state['user_type'] == 'User':

            if 'otp_verified' not in st. session_state:
                st.session_state['otp_verified'] = False
            
            if not st.session_state['otp_verified']:

                st.markdown("""
                    #### Bienvenid@ a la sección de administración. Esta página está diseñada exclusivamente para el acceso y la gestión por parte de usuarios autorizados.

                    ## Información Sensible

                    Es importante destacar que esta área contiene información sensible sobre migrantes. Debido a la naturaleza delicada de los datos, se implementan medidas estrictas de seguridad y encriptación para proteger esta información.

                    ### Acceso Restringido

                    **Si usted está aquí, es porque ha sido verificado y autorizado para manejar dichos datos. Le pedimos proceder con la máxima precaución y responsabilidad.**

                    ### Responsabilidad

                    Usted tiene la responsabilidad de:
                    - **Proteger la confidencialidad y la integridad de la información.**
                    - **Asegurar que el acceso a los datos se realice de forma segura y solo cuando sea estrictamente necesario.**

                    Agradezemos su compromiso con la seguridad y el respeto por la privacidad de los individuos cuyos datos están a nuestro cuidado.
                """)

                st.warning("Ingrese la OTP para acceder a esta página")
                opt_input = st.text_input("OTP", type = "password")

                #dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
                #load_dotenv(dotenv_path=dotenv_path)
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

                #dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
                #load_dotenv(dotenv_path=dotenv_path)
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
                # Filtrar los migrantes según el estado actual o pasado
                if 'consult' not in st.session_state:
                    st.info("En esta sección podrás consultar información sobre todos los migrantes que han pasado por Casa Monarca.")
                    st.markdown("""
                                                
                    ### Migrantes actuales:
                    Aquí podrás consultar información sobre todos los migrantes que actualmente están en Casa Monarca.
                    Si es necesario, podrás dar de baja a cualquier migrante proporcionando una razón para ello.
                                    
                    ### Migrantes pasados:
                    Aquí podrás consultar información sobre todos los migrantes que estuvieron en Casa Monarca por un tiempo.

                    ### Filtros de selección:
                    Podrás filtrar la búsqueda mediante dos opciones: nombre completo o un rango de fechas a consultar.
                                
                    **Una vez que hayas seleccionado a la persona de interés, haz click en el botón 'Consultar información'.
                    Cuando se haya finalizado la consulta o se quiera consultar a otro migrante, haz click en el botón 'Finalizar consulta'.**
                    """)

                    migrant_type = st.selectbox('Seleccione el tipo de migrantes', ['Actuales', 'Pasados'])
                    st.session_state['migrant_type'] = migrant_type  # Guarda el tipo de migrante seleccionado
                    
                    if migrant_type == 'Actuales':
                        df_filtered = df[df['current_member'] == 'si']
                        search_type = st.selectbox('Seleccione el método de búsqueda', ['Seleccione', 'Nombre completo', 'Fecha de registro'])
                    else:
                        df_filtered = df[df['current_member'] == 'no']
                        search_type = st.selectbox('Seleccione el método de búsqueda', ['Seleccione', 'Nombre completo', 'Fecha de salida'])

                    selected_migrant = None
                    selected_id = None

                    if search_type == 'Nombre completo':
                        all_names = df_filtered['full_name'].unique()
                        selected_migrant = st.selectbox('Seleccione un nombre', ['Seleccione'] + list(all_names))
                        dummy_df = df[(df['full_name'] == selected_migrant)]
                        try: 
                            st.image(base64.b64decode(dummy_df['front_photo'].values[0]), caption='Foto de frente')
                        except IndexError:
                            st.write(" ")
                        if selected_migrant != 'Seleccione':
                            ids_for_name = df_filtered[df_filtered['full_name'] == selected_migrant]['id'].unique()
                            if len(ids_for_name) > 1:
                                st.write(f"Parece que hay múltiples registros bajo el nombre {selected_migrant}")
                                selected_id = st.selectbox('Seleccione el ID', ['Seleccione'] + list(ids_for_name))
                            else:
                                selected_id = ids_for_name[0]

                    elif search_type in ['Fecha de registro', 'Fecha de salida']:
                        if migrant_type == 'Actuales':
                            min_date = pd.to_datetime(df_filtered['arrival_date'].min()).date()
                            max_date = pd.to_datetime(df_filtered['arrival_date'].max()).date()
                        else:
                            df_filtered['date_departure'] = pd.to_datetime(df_filtered['date_departure']).dt.date
                            min_date = pd.to_datetime(df_filtered['date_departure'].min()).date()
                            max_date = pd.to_datetime(df_filtered['date_departure'].max()).date()
                        
                        date_range = st.date_input('Seleccione un rango de fechas', [min_date, max_date], min_value=min_date, max_value=max_date)

                        if date_range:
                            start_date, end_date = date_range
                            if migrant_type == 'Actuales':
                                filtered_df = df_filtered[(df_filtered['arrival_date'] >= start_date) & (df_filtered['arrival_date'] <= end_date)]
                            else:
                                filtered_df = df_filtered[(df_filtered['date_departure'] >= start_date) & (df_filtered['date_departure'] <= end_date)]

                            selected_name = st.selectbox('Seleccione un nombre', ['Seleccione'] + filtered_df['full_name'].tolist())
                            if selected_name != 'Seleccione':
                                selected_id = filtered_df[filtered_df['full_name'] == selected_name]['id'].values[0]
                                selected_migrant = selected_name
                                dummy_df = df[(df['full_name'] == selected_migrant)]
                                try: 
                                    st.image(base64.b64decode(dummy_df['front_photo'].values[0]), caption='Foto de frente')
                                except IndexError:
                                    st.write(" ")

                    # Apretamos el boton para consultar la consulta
                    if selected_migrant and selected_id and st.button('Consultar información', key='consultar_info'):
                        st.session_state['selected_migrant'] = selected_migrant
                        st.session_state['selected_id'] = selected_id
                        st.session_state['consult'] = True

                        # Debemos registrar en los logs la consulta realizada
                        with SessionLocal() as session:
                            log_entry = Logs(
                                action="Migrant information",
                                user_name=st.session_state['username'],  # Nombre de usuario del admin que crea el usuario
                                user_type=st.session_state['user_type'], # Los permisos de usuario (admin unicamente)
                                description=f"Usuario '{st.session_state['username']}' con ID '{st.session_state['id']}' consultó información de migrante: '{selected_migrant}'." # descripcion de lo sucedido
                            )
                            session.add(log_entry)
                            session.commit()

                        st.rerun()

                if st.session_state.get('consult'):
                    st.markdown("""
                        ### Consulta de Información

                        En esta sección podrás consultar información detallada sobre los migrantes en cuatro rubros diferentes:

                        * **General**: Aquí encontrarás información básica y demográfica de los migrantes, incluyendo datos personales y de contacto.
                        * **Educación**: En esta categoría se recopila información sobre el nivel educativo, habilidades lingüísticas y formación académica de los migrantes.
                        * **Salud**: Este apartado incluye datos relacionados con el estado de salud, historial médico, tratamientos actuales y cualquier condición médica relevante.
                        * **Tránsito**: Aquí se detallan los datos sobre el tránsito del migrante, incluyendo rutas de viaje, medios de transporte, y experiencias durante el trayecto.

                        Utiliza los filtros disponibles para encontrar y consultar la información específica que necesitas.
                        """)
                    selected_id = st.session_state['selected_id']
                    selected_migrant = st.session_state['selected_migrant']
                    migrant_type = st.session_state['migrant_type']  # Recupera el tipo de migrante seleccionado
                    st.info(f'Consulta de información sobre {selected_migrant}')
                    # Verificar la condición de refugiado
                    df_migrant = df[(df['full_name'] == selected_migrant) & (df['id'] == selected_id)]
                    # Verificar la condición de refugiado
                    if df_migrant['refugee'].values[0] == 'Sí':
                        st.markdown("""
                            ### Acciones para Migrantes en Condición de Refugiado

                            Si el migrante se encuentra en condición de refugiado, puedes realizar las siguientes acciones adicionales:

                            * **Actualizar Servicios Proporcionados**: Modifica y actualiza la lista de servicios que han sido proporcionados al migrante.
                        """)
                    if df_migrant['refugee'].values[0] == 'Sí':
                        st.info("**Condición:** Refugiado")
                    else:
                        st.info("**Condición:** En tránsito")
                    # Crear tres columnas
                    col1, col2, col3 = st.columns(3)

                    # Mostrar las imágenes en las columnas correspondientes
                    with col1:
                        st.image(base64.b64decode(df_migrant['front_photo'].values[0]), caption='Foto de frente')

                    with col2:
                        st.image(base64.b64decode(df_migrant['right_profile_photo'].values[0]), caption='Foto de perfil derecho')

                    with col3:
                        st.image(base64.b64decode(df_migrant['left_profile_photo'].values[0]), caption='Foto de perfil izquierdo')
                    st.markdown("### Seleccione el tipo de dato a Consultar")
                    data_type = st.selectbox('Consulta sobre',['Seleccione', 'General', 'Health', 'Transit', 'Education'])

                    if data_type != 'Seleccione':
                        if data_type == 'General':
                            columnas = [col for col in df_migrant.columns if not any(prefix in col for prefix in ['transit', 'health', 'education'])]
                            columnas.remove('full_name')
                            columnas.remove('front_photo')
                            columnas.remove('right_profile_photo')
                            columnas.remove('left_profile_photo')
                            if migrant_type == 'Actuales':
                                columnas.remove('date_departure') 
                                columnas.remove('reason_departure')
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

                    # Bloque para actualizar los servicios proporcionados a un migrante refugiado
                    if df_migrant['refugee'].values[0] == 'Sí' and migrant_type == "Actuales":
                        st.markdown("### Actualización de Servicios Proporcionados")

                        # Servicios que se ofrecen a personas con solicitud/condición de refugiado
                        services_refugee = [
                            'Orientaciones Legales',
                            'Asesorías legales',
                            'Trámite CURP',
                            'Obtención RFC',
                            'Obtención NSS',
                            'Afiliación IMSS',
                            'Acceso a vivienda',
                            'Apertura Cta. Bancaria',
                            'Atención médica (Acompañamiento)',
                            'Revalidación de estudios (Acompañamiento)',
                            'Vinculación Educativa (Escolaridad obligatoria)',
                            'Capacitación técnica certificada (acompañamiento)',
                            'Canalización para recepción de apoyo para la capacitación',
                            'Capacitación / Orientación para ingresar al mercado laboral',
                            'Canalización a empresa u organización especializada para la vinculación laboral',
                            'Canalización a una empresa',
                            'Canalización al SNE',
                            'Canalización a una bolsa de empleo',
                            'Canalización a organización especializada para el empleo',
                            'Necesidad específica de protección',
                            'Recibieron atención psicológica y psicosocial fuera del albergue',
                            'Identificación de necesidades psicosocial, orientación y canalización',
                            'Acompañamiento para acceso a servicios',
                            'Primeros auxilios psicológicos',
                            'Psicoterapia (individual/familiar)',
                            'Psicoterapia Grupal',
                            'Talleres psicoeducativos',
                            'Canalización a servicios de psiquiatría'
                        ]

                        # Servicios ya proporcionados
                        existing_services = df_migrant['services_provided'].values[0].split(', ') if 'services_provided' in df_migrant.columns else []

                        # Filtrar servicios ya proporcionados para no mostrarlos en el multiselect
                        available_services = [service for service in services_refugee if service not in existing_services]

                        # Formulario para actualizar servicios proporcionados
                        with st.form(key='update_services_form'):
                            new_services_provided = st.multiselect(
                                "¿Cuáles servicios se le brindaron a la persona?",
                                options=available_services
                            )
                            confirmar_servicios = st.form_submit_button('Actualizar Servicios')

                            if confirmar_servicios:
                                # Unir los nuevos servicios con los ya existentes
                                all_services_provided = existing_services + new_services_provided

                                with SessionLocal() as session:
                                    migrant = session.query(General).filter(General.id == int(selected_id)).first()
                                    if migrant:
                                        public_key_base64 = os.getenv('PUBLIC_KEY')
                                        public_key_pem = base64.b64decode(public_key_base64)
                                        PUBLIC_KEY = load_pem_public_key(public_key_pem)
                                        services_str = ', '.join(all_services_provided)
                                        migrant.services_provided = encrypt_data(PUBLIC_KEY,services_str)
                                        
                                        # Registrar en los logs la actualización de servicios
                                        log_entry = Logs(
                                            action="Migrant information",
                                            user_name=st.session_state['username'],
                                            user_type=st.session_state['user_type'],
                                            description=f"Usuario '{st.session_state['username']}' con ID '{st.session_state['id']}' actualizó los servicios proporcionados a migrante: '{selected_migrant}'."
                                        )
                                        session.add(log_entry)
                                        session.commit()

                                    st.success('Servicios proporcionados actualizados exitosamente.')
                                    del st.session_state['selected_migrant']
                                    del st.session_state['selected_id']
                                    del st.session_state['consult']
                                    del st.session_state['migrant_type']
                                    time.sleep(1)
                                    st.rerun()

                    if migrant_type == 'Actuales':
                        st.markdown("### Dar de baja")
                        with st.form(key='dar_de_baja_form'):
                            reason_departure = st.text_input('Razón de baja')
                            today = datetime.today().date()
                            arrival_date = df_migrant['arrival_date'].values[0]
                            date_departure = st.date_input('Fecha de salida', min_value=arrival_date, max_value=today)
                            confirmar_baja = st.form_submit_button('Confirmar baja')
                            if confirmar_baja:
                                if reason_departure:
                                    public_key_base64 = os.getenv('PUBLIC_KEY')
                                    public_key_pem = base64.b64decode(public_key_base64)
                                    PUBLIC_KEY = load_pem_public_key(public_key_pem)

                                    with SessionLocal() as session:
                                        migrant = session.query(General).filter(General.id == int(selected_id)).first()
                                        if migrant:
                                            migrant.current_member = encrypt_data(PUBLIC_KEY, 'no')
                                            migrant.reason_departure = encrypt_data(PUBLIC_KEY, reason_departure)
                                            migrant.date_departure = encrypt_data(PUBLIC_KEY, date_departure.strftime('%Y-%m-%d'))
                                            
                                            # Igual debemos registrar esta información en los LOGS!
                                            log_entry = Logs(
                                                action="Migrant information",
                                                user_name=st.session_state['username'],  # Nombre de usuario del admin que dio de baja al migrante
                                                user_type=st.session_state['user_type'],
                                                description=f"Usuario '{st.session_state['username']}' con ID '{st.session_state['id']}' dio de baja a migrante: '{selected_migrant} '." 
                                            )

                                            session.add(log_entry)

                                            session.commit()

                                        st.success('Migrante dado de baja exitosamente.')
                                        del st.session_state['selected_migrant']
                                        del st.session_state['selected_id']
                                        del st.session_state['consult']
                                        del st.session_state['migrant_type']  # Elimina el tipo de migrante seleccionado
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.error('Por favor, proporciona una razón de baja.')

                    if st.button('Finalizar consulta', key='finalizar_consulta'):
                        del st.session_state['selected_migrant']
                        del st.session_state['selected_id']
                        del st.session_state['consult']
                        del st.session_state['migrant_type']  # Elimina el tipo de migrante seleccionado
                        st.rerun()
        
        elif st.session_state.get('authenticated') and st.session_state['user_type'] == 'Colaborador':
            st.error('No tienes permisos para acceder a esta página.')
        
        # en teoria este mensaje nunca sale
        else:
            st.error('Favor de iniciar sesión para acceder a esta página.')
