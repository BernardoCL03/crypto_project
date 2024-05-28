import os
import streamlit as st
import base64
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from back.encrypt import decrypt_data
from sqlalchemy.orm import joinedload
import pandas as pd
# our decrypt data function
from back.encrypt import admin_decrypt_page

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

if st.session_state.get('authenticated'):
    st.sidebar.write(f"Usuario: {st.session_state['username']}")
    st.sidebar.write(f"Permisos: {st.session_state['user_type']}")
    if st.sidebar.button("Cerrar sesión"):
        # Al hacer clic en cerrar sesión, cambiamos el estado a no autenticado
        st.session_state.authenticated = False

st.title("Dashboard de Datos")

if st.session_state.get('authenticated'):
        if st.session_state['user_type'] == 'Admin' or st.session_state['user_type'] == 'User':

            # Desencriptar todos los datos
            dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
            load_dotenv(dotenv_path=dotenv_path)
            TOTP_SECRET = os.getenv("TOTP_SECRET")

            # leemos en formato base64, tenemos que convertirla a objeto valido
            private_key_base64 = os.getenv('PRIVATE_KEY')
            private_key_pem = base64.b64decode(private_key_base64)
            PRIVATE_KEY = load_pem_private_key(private_key_pem, password=TOTP_SECRET.encode())
            data = admin_decrypt_page(PRIVATE_KEY)
            df = pd.json_normalize(data, sep='_')
            st.info('Cantidad de migrantes en Casa Monarca')
            st.markdown(f"""
            <div style='background-color:#000000; border: 1px solid #dcdcdc; padding: 5px; border-radius: 5px; text-align: center;'>
                <h2 style='font-size: 48px;'>{len(df)} </h2>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            st.info('Filtros para dashboards')
            dictFilters = {}
            variables = [
                "arrival_date", "type", "gender", "age", "country_of_origin", "civil_status",
                "has_children", "children_traveling", "can_return_to_country", "access_to_casa_monarca",
                "services_provided", "assigned_dormitory", "date_left_origin", "traveling_alone_accompanied",
                "who_accompanied", "abuse_during_travel", "abuse_in_mexico", "paid_guide", "amount_paid",
                "date_entered_mexico", "entry_point_mexico", "final_destination", "destination_monterrey",
                "support_network_monterrey", "tried_enter_us", "support_network_us", "been_in_migration_station",
                "suffered_aggression", "description_of_facts", "filed_complaint", "stayed_in_shelter",
                "has_illness", "on_medical_treatment", "medical_treatment_description", "has_allergy",
                "is_pregnant", "months_pregnant", "has_prenatal_care", "can_read_write", "last_grade_study",
                "languages_spoken", "other_language"
            ]
            dictFilters = {}
            for column in df.columns.tolist():
                if column in variables:
                    dictFilters[column] = list(df[column].unique())

            if 'filters' not in st.session_state:
                st.session_state['filters'] = []

            if st.button("Agregar filtro"):
                # Add a new filter slot
                st.session_state['filters'].append({})

            for i, filter_dict in enumerate(st.session_state['filters']):
                with st.container():
                    key = st.selectbox(
                        'Seleccione la clave del filtro:',
                        options=list(dictFilters.keys()),
                        key=f'key_select_{i}'
                    )
                    if key:
                        value = st.selectbox(
                            'Seleccione el valor:',
                            options=dictFilters[key],
                            key=f'value_select_{i}'
                        )
                        # Update the dictionary for the current filter
                        st.session_state['filters'][i] = {key: value}

            # Apply filters to the dataframe
            if st.button("Aplicar filtros"):
                df_filtered = df.copy()
                for filter_dict in st.session_state['filters']:
                    for k, v in filter_dict.items():
                        df_filtered = df_filtered[df_filtered[k] == v]
                # Display filtered dataframe
                st.write(df_filtered)






else:
     st.error('Favor de iniciar sesión para acceder a esta página.')

