import os
import streamlit as st
import base64
import pyotp
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from back.encrypt import decrypt_data
from back.model import SessionLocal, General, Transit, Health, Education
from sqlalchemy.orm import joinedload
import pandas as pd
# our decrypt data function
from back.encrypt import decrypt_data, decrypt_large_data

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

if st.session_state.get('authenticated'):
    st.sidebar.write(f"Usuario: {st.session_state['username']}")
    st.sidebar.write(f"Permisos: {st.session_state['user_type']}")
    if st.sidebar.button("Cerrar sesión"):
        # Al hacer clic en cerrar sesión, cambiamos el estado a no autenticado
        st.session_state.authenticated = False

# función para desencriptar todos los dataos guardados en la base de datos
def admin_decrypt_page(private_key):
    with SessionLocal() as session:
        general_query = session.query(General).all()
        transit_query = {transit.id: transit for transit in session.query(Transit).all()}
        health_query = {health.id: health for health in session.query(Health).all()}
        education_query = {education.id: education for education in session.query(Education).all()}

        data = []
        for migrant in general_query:
            transit = transit_query.get(migrant.id, {})
            health = health_query.get(migrant.id, {})
            education = education_query.get(migrant.id, {})
            
            decrypted_migrant = {
                'id': migrant.id,
                'arrival_date': decrypt_data(private_key, migrant.arrival_date),
                'type': decrypt_data(private_key, migrant.type),
                'name': decrypt_data(private_key, migrant.name),
                'last_name': decrypt_data(private_key, migrant.last_name),
                'gender': decrypt_data(private_key, migrant.gender),
                'birth_date': decrypt_data(private_key, migrant.birth_date),
                'age': decrypt_data(private_key, migrant.age),
                'country_of_origin': decrypt_data(private_key, migrant.country_of_origin),
                'civil_status': decrypt_data(private_key, migrant.civil_status),
                'has_children': decrypt_data(private_key, migrant.has_children),
                'children_traveling': decrypt_data(private_key, migrant.children_traveling),
                'can_return_to_country': decrypt_data(private_key, migrant.can_return_to_country),
                'reason_cannot_return': decrypt_data(private_key, migrant.reason_cannot_return),
                'access_to_casa_monarca': decrypt_data(private_key, migrant.access_to_casa_monarca),
                'reason_for_denial': decrypt_data(private_key, migrant.reason_for_denial),
                'services_provided': decrypt_data(private_key, migrant.services_provided),
                'assigned_dormitory': decrypt_data(private_key, migrant.assigned_dormitory),
                'distinctive_signs': decrypt_data(private_key, migrant.distinctive_signs),
                'emergency_contact': decrypt_data(private_key, migrant.emergency_contact),
                'emergency_contact_location': decrypt_data(private_key, migrant.emergency_contact_location),
                'final_observations': decrypt_data(private_key, migrant.final_observations),
                'front_photo': decrypt_large_data(private_key, migrant.front_photo) if migrant.front_photo else None,
                'right_profile_photo': decrypt_large_data(private_key, migrant.right_profile_photo) if migrant.right_profile_photo else None,
                'left_profile_photo': decrypt_large_data(private_key, migrant.left_profile_photo) if migrant.left_profile_photo else None,
                'transit': {
                    'date_left_origin': decrypt_data(private_key, transit.date_left_origin),
                    'traveling_alone_accompanied': decrypt_data(private_key, transit.traveling_alone_accompanied),
                    'who_accompanied': decrypt_data(private_key, transit.who_accompanied),
                    'which_relative': decrypt_data(private_key, transit.which_relative),
                    'how_traveled': decrypt_data(private_key, transit.how_traveled),
                    'reason_for_leaving': decrypt_data(private_key, transit.reason_for_leaving),
                    'abuse_during_travel': decrypt_data(private_key, transit.abuse_during_travel),
                    'type_of_abuse': decrypt_data(private_key, transit.type_of_abuse),
                    'abuse_in_mexico': decrypt_data(private_key, transit.abuse_in_mexico),
                    'type_of_abuse_mexico': decrypt_data(private_key, transit.type_of_abuse_mexico),
                    'abuser': decrypt_data(private_key, transit.abuser),
                    'paid_guide': decrypt_data(private_key, transit.paid_guide),
                    'amount_paid': decrypt_data(private_key, transit.amount_paid),
                    'date_entered_mexico': decrypt_data(private_key, transit.date_entered_mexico),
                    'entry_point_mexico': decrypt_data(private_key, transit.entry_point_mexico),
                    'final_destination': decrypt_data(private_key, transit.final_destination),
                    'destination_monterrey': decrypt_data(private_key, transit.destination_monterrey),
                    'reason_stay_monterrey': decrypt_data(private_key, transit.reason_stay_monterrey),
                    'support_network_monterrey': decrypt_data(private_key, transit.support_network_monterrey),
                    'time_knowing_support': decrypt_data(private_key, transit.time_knowing_support),
                    'tried_enter_us': decrypt_data(private_key, transit.tried_enter_us),
                    'support_network_us': decrypt_data(private_key, transit.support_network_us),
                    'description_support_us': decrypt_data(private_key, transit.description_support_us),
                    'been_in_migration_station': decrypt_data(private_key, transit.been_in_migration_station),
                    'suffered_aggression': decrypt_data(private_key, transit.suffered_aggression),
                    'migration_station_location': decrypt_data(private_key, transit.migration_station_location),
                    'description_of_facts': decrypt_data(private_key, transit.description_of_facts),
                    'filed_complaint': decrypt_data(private_key, transit.filed_complaint),
                    'reason_no_complaint': decrypt_data(private_key, transit.reason_no_complaint),
                    'solution_offered': decrypt_data(private_key, transit.solution_offered),
                    'stayed_in_shelter': decrypt_data(private_key, transit.stayed_in_shelter),
                    'last_shelter': decrypt_data(private_key, transit.last_shelter),
                },
                'health': {
                    'has_illness': decrypt_data(private_key, health.has_illness),
                    'illness_details': decrypt_data(private_key, health.illness_details),
                    'on_medical_treatment': decrypt_data(private_key, health.on_medical_treatment),
                    'medical_treatment_description': decrypt_data(private_key, health.medical_treatment_description),
                    'has_allergy': decrypt_data(private_key, health.has_allergy),
                    'allergy_details': decrypt_data(private_key, health.allergy_details),
                    'is_pregnant': decrypt_data(private_key, health.is_pregnant),
                    'months_pregnant': decrypt_data(private_key, health.months_pregnant),
                    'has_prenatal_care': decrypt_data(private_key, health.has_prenatal_care),
                },
                'education': {
                    'can_read_write': decrypt_data(private_key, education.can_read_write),
                    'last_grade_study': decrypt_data(private_key, education.last_grade_study),
                    'languages_spoken': decrypt_data(private_key, education.languages_spoken),
                    'other_language': decrypt_data(private_key, education.other_language),
                }
            }
            data.append(decrypted_migrant)

        return data


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
        