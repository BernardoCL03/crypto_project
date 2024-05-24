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
from back.encrypt import decrypt_data

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
                'transit': {
                    'date_left_origin': getattr(transit, 'date_left_origin', None),
                    'traveling_alone_accompanied': getattr(transit, 'traveling_alone_accompanied', None),
                    'who_accompanied': getattr(transit, 'who_accompanied', None),
                    'which_relative': getattr(transit, 'which_relative', None),
                    'how_traveled': getattr(transit, 'how_traveled', None),
                    'reason_for_leaving': getattr(transit, 'reason_for_leaving', None),
                    'abuse_during_travel': getattr(transit, 'abuse_during_travel', None),
                    'type_of_abuse': getattr(transit, 'type_of_abuse', None),
                    'abuse_in_mexico': getattr(transit, 'abuse_in_mexico', None),
                    'type_of_abuse_mexico': getattr(transit, 'type_of_abuse_mexico', None),
                    'abuser': getattr(transit, 'abuser', None),
                    'paid_guide': getattr(transit, 'paid_guide', None),
                    'amount_paid': getattr(transit, 'amount_paid', None),
                    'date_entered_mexico': getattr(transit, 'date_entered_mexico', None),
                    'entry_point_mexico': getattr(transit, 'entry_point_mexico', None),
                    'final_destination': getattr(transit, 'final_destination', None),
                    'destination_monterrey': getattr(transit, 'destination_monterrey', None),
                    'reason_stay_monterrey': getattr(transit, 'reason_stay_monterrey', None),
                    'support_network_monterrey': getattr(transit, 'support_network_monterrey', None),
                    'time_knowing_support': getattr(transit, 'time_knowing_support', None),
                    'tried_enter_us': getattr(transit, 'tried_enter_us', None),
                    'support_network_us': getattr(transit, 'support_network_us', None),
                    'description_support_us': getattr(transit, 'description_support_us', None),
                    'been_in_migration_station': getattr(transit, 'been_in_migration_station', None),
                    'suffered_aggression': getattr(transit, 'suffered_aggression', None),
                    'migration_station_location': getattr(transit, 'migration_station_location', None),
                    'description_of_facts': getattr(transit, 'description_of_facts', None),
                    'filed_complaint': getattr(transit, 'filed_complaint', None),
                    'reason_no_complaint': getattr(transit, 'reason_no_complaint', None),
                    'solution_offered': getattr(transit, 'solution_offered', None),
                    'stayed_in_shelter': getattr(transit, 'stayed_in_shelter', None),
                    'last_shelter': getattr(transit, 'last_shelter', None),
                },
                'health': {
                    'has_illness': getattr(health, 'has_illness', None),
                    'illness_details': getattr(health, 'illness_details', None),
                    'on_medical_treatment': getattr(health, 'on_medical_treatment', None),
                    'medical_treatment_description': getattr(health, 'medical_treatment_description', None),
                    'has_allergy': getattr(health, 'has_allergy', None),
                    'allergy_details': getattr(health, 'allergy_details', None),
                    'is_pregnant': getattr(health, 'is_pregnant', None),
                    'months_pregnant': getattr(health, 'months_pregnant', None),
                    'has_prenatal_care': getattr(health, 'has_prenatal_care', None),
                },
                'education': {
                    'can_read_write': getattr(education, 'can_read_write', None),
                    'last_grade_study': getattr(education, 'last_grade_study', None),
                    'languages_spoken': getattr(education, 'languages_spoken', None),
                    'other_language': getattr(education, 'other_language', None),
                }
            }
            data.append(decrypted_migrant)

        return data

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

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
                    st.experimental_rerun()
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
            all_names = df['full_name'].unique()
            # Crear un menú desplegable con los nombres
        
            selected_migrant = st.selectbox('Seleccione un nombre', ['Seleccione'] + list(all_names))
            
            if selected_migrant != 'Seleccione':
                 data_type = st.selectbox('Seleccione el tipo de dato', ['Seleccione','General', 'Health', 'Transit', 'Education'])
                 
                 if data_type != 'Seleccione':
                    # Filtrar el DataFrame según el nombre seleccionado
                    df_migrant = df[df['full_name'] == selected_migrant]

                    if data_type == 'General':
                        columnas = [col for col in df_migrant.columns if not any(prefix in col for prefix in ['transit', 'health', 'education'])]
                        columnas.remove('full_name')
                    elif data_type == 'Health':
                        columnas = [col for col in df_migrant.columns if 'health' in col]
                    elif data_type == 'Transit':
                        columnas = [col for col in df_migrant.columns if 'transit' in col]
                    elif data_type == 'Education':
                        columnas = [col for col in df_migrant.columns if 'education' in col]
                    # Mostrar el DataFrame filtrado sin el índice
                    
                    df_seleccionado = df_migrant[columnas]
                    # Transponer el DataFrame
                    df_transpuesto = df_seleccionado.transpose()

                    # Corregir los nombres de las columnas
                    df_transpuesto.columns = [selected_migrant]

                    st.dataframe(df_transpuesto, width=1200, height=600)
    
    elif st.session_state.get('authenticated') and st.session_state['user_type'] == 'User':
        st.error('No tienes permisos para acceder a esta página.')
    
    else:
        st.error('Favor de iniciar sesión.')
        