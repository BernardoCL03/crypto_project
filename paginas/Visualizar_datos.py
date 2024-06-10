import datetime
import os
import streamlit as st
import base64
#from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import pandas as pd
import plotly.express as px


# our decrypt data function
from back.encrypt import admin_decrypt_page

#st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def visualizar_datos_page():

    st.title("Dashboard de Datos")

    if st.session_state.get('authenticated'):
            if st.session_state['user_type'] == 'Admin' or st.session_state['user_type'] == 'User':

                # Desencriptar todos los datos
                #dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
                #load_dotenv(dotenv_path=dotenv_path)
                TOTP_SECRET = os.getenv("TOTP_SECRET")

                # leemos en formato base64, tenemos que convertirla a objeto valido
                private_key_base64 = os.getenv('PRIVATE_KEY')
                private_key_pem = base64.b64decode(private_key_base64)
                PRIVATE_KEY = load_pem_private_key(private_key_pem, password=TOTP_SECRET.encode())
                data = admin_decrypt_page(PRIVATE_KEY)
                df = pd.json_normalize(data, sep='_')
                df = df[df['current_member'] == 'si']
    
                st.sidebar.info(f"Cantidad de migrantes actualmente en Casa Monarca: *{len(df)}*")

                variables = [
                    "arrival_date", "type", "gender", "age", "country_of_origin", "civil_status",
                    "has_children", "children_traveling", "can_return_to_country", "access_to_casa_monarca",
                    "assigned_dormitory", "date_left_origin", "traveling_alone_accompanied",
                    "who_accompanied", "abuse_during_travel", "abuse_in_mexico", "paid_guide", "amount_paid",
                    "date_entered_mexico", "entry_point_mexico", "final_destination", "destination_monterrey",
                    "support_network_monterrey", "tried_enter_us", "support_network_us", "been_in_migration_station",
                    "suffered_aggression", "description_of_facts", "filed_complaint", "stayed_in_shelter",
                    "has_illness", "on_medical_treatment", "medical_treatment_description", "has_allergy",
                    "is_pregnant", "months_pregnant", "has_prenatal_care", "can_read_write", "last_grade_study",
                    "languages_spoken", "other_language"
                ]

                filters = {}
                for key in variables:
                    if key in df.columns:
                        unique_vals = df[key].dropna().unique()
                        if len(unique_vals) > 1:
                            if df[key].dtype == 'int64':
                                min_val, max_val = int(df[key].min()), int(df[key].max())
                                value_range = st.sidebar.slider(f"{key} (rango)", min_val, max_val, (min_val, max_val))
                                filters[key] = (df[key] >= value_range[0]) & (df[key] <= value_range[1])
                            elif pd.api.types.is_datetime64_any_dtype(df[key]):
                                min_val, max_val = df[key].min(), df[key].max()
                                date_range = st.sidebar.date_input(f"{key} (rango)", [min_val, max_val])
                                filters[key] = (df[key] >= date_range[0]) & (df[key] <= date_range[1])
                            else:
                                value = st.sidebar.selectbox(f"{key}", ['Todos'] + list(unique_vals))
                                if value != 'Todos':
                                    filters[key] = (df[key] == value)
                        elif len(unique_vals) == 1:
                            st.sidebar.markdown(f"{key} tiene un único valor: {unique_vals[0]} (no se necesita filtro)")

                if filters:
                    for key, filter_condition in filters.items():
                        df = df[filter_condition]

                # Crear dos columnas para visualizar las gráficas
                cols = st.columns(2)
                col_index = 0

                # Colores sólidos para las gráficas
                color_crimson = ["crimson"]

                for variable in variables:
                    if variable in df.columns:
                        if df[variable].dtype in ['int64', pd.api.types.is_datetime64_any_dtype(df[variable])]:
                            fig = px.histogram(df, x=variable, title=f'Distribución de {variable}', color_discrete_sequence=color_crimson)
                        else:
                            # Contando los valores correctamente para categorías
                            data_to_plot = df[variable].value_counts().reset_index()
                            data_to_plot.columns = ['category', 'count']
                            fig = px.bar(data_to_plot, x='category', y='count', title=f'Frecuencia de {variable}', color_discrete_sequence=color_crimson)

                        if fig:
                            cols[col_index].plotly_chart(fig, use_container_width=True)
                            col_index = (col_index + 1) % 2  # Alternar entre las dos columnas


    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')

