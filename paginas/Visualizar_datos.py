import datetime
import os
import streamlit as st
import base64
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import matplotlib.pyplot as plt
import seaborn as sns
import math
import pandas as pd

# our decrypt data function
from back.encrypt import admin_decrypt_page

#st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def visualizar_datos_page():

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
                df = df[df['current_member'] == 'si']
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
                            # Determine the type of data in the column
                            if df[key].dtype == 'int64':
                                # It's an integer, use a slider
                                value_range = st.slider(
                                    "Seleccione el rango de valores:",
                                    min_value=int(df[key].min()),
                                    max_value=int(df[key].max()),
                                    value=(int(df[key].min()), int(df[key].max())),
                                    key=f'range_slider_{i}'
                                )
                                # Update the dictionary to filter between this range
                                st.session_state['filters'][i] = {key: value_range}
                            elif isinstance(df[key].iloc[0], datetime.date):
                                # It's a datetime, use a date input
                                date_range = st.slider(
                                    "Seleccione el rango de valores:",
                                    min_value=(df[key].min()),
                                    max_value=(df[key].max()),
                                    value=((df[key].min()), (df[key].max())),
                                    key=f'range_slider_{i}'
                                )
                                st.session_state['filters'][i] = {key: date_range}
                            else:
                                # It's categorical or other, use a selectbox
                                value = st.selectbox(
                                    'Seleccione el valor:',
                                    options=pd.unique(df[key].dropna()),
                                    key=f'value_select_{i}'
                                )
                                st.session_state['filters'][i] = {key: value}

                # Apply filters to the dataframe
                if st.button("Aplicar filtros"):
                    df_filtered = df.copy()
                    for filter_dict in st.session_state['filters']:
                        for k, v in filter_dict.items():
                            if isinstance(v, tuple) and isinstance(v[0], int):
                                df_filtered = df_filtered[(df_filtered[k] >= v[0]) & (df_filtered[k] <= v[1])]
                            elif isinstance(v, tuple) and isinstance(v[0], pd.Timestamp):
                                df_filtered = df_filtered[(df_filtered[k] >= v[0]) & (df_filtered[k] <= v[1])]
                            else:
                                df_filtered = df_filtered[df_filtered[k] == v]
                    # Display filtered dataframe
                    df = df_filtered

                # After the line 'st.write(df_filtered)'
                # Define the number of columns in the grid
                num_columns = 3  # You can change this number based on your preference or screen size
                print(plt.style.available)
                plt.style.use('seaborn-v0_8-darkgrid')
                plt.rcParams['axes.facecolor'] = 'none'  # Dark grey background for the axes
                plt.rcParams['figure.facecolor'] = 'none'  # Darker grey background for the figure
                plt.rcParams['axes.edgecolor'] = 'white'  # White edges to better delimit the plots
                plt.rcParams['text.color'] = 'white'  # White text for better contrast
                plt.rcParams['axes.labelcolor'] = 'white'
                plt.rcParams['xtick.color'] = 'white'
                plt.rcParams['ytick.color'] = 'white'

                # Assume df is your DataFrame, also predefined
                figures = []  # This will hold the figures to display later

                for variable in variables:
                    if variable in df.columns:
                        fig, ax = plt.subplots(figsize=(10, 6))  # Larger figure size for better readability
                        if df[variable].dtype == 'int64':
                            # Plotting for integer variables with a nicer palette and edges
                            sns.histplot(df[variable].dropna(), kde=True, color='skyblue', edgecolor='black', ax=ax)
                            ax.set_title(f'Distribution of {variable}', fontsize=16)
                        elif isinstance(df[variable].iloc[0], datetime.date):
                            # Plotting for date variables with a line plot
                            date_counts = df[variable].dropna().value_counts().sort_index()
                            date_counts.plot(kind='line', color='green', ax=ax)
                            ax.set_title(f'Time Series of {variable}', fontsize=16)
                            ax.set_xlabel('Date', fontsize=12)
                            ax.set_ylabel('Frequency', fontsize=12)
                        else:
                            # Plotting for object variables with better visual handling of categories
                            value_counts = df[variable].value_counts()
                            sns.barplot(x=value_counts.index, y=value_counts.values, palette='viridis', ax=ax)
                            ax.set_title(f'Frequency of {variable}', fontsize=16)
                            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
                        ax.set_xlabel(ax.get_xlabel(), fontsize=12)
                        ax.set_ylabel(ax.get_ylabel(), fontsize=12)
                        ax.tick_params(labelsize=10)  # Smaller label size
                        figures.append(fig)  # Append the figure to the list

                # Assume you have a Streamlit setup with num_columns defined
                num_rows = math.ceil(len(figures) / num_columns)  # Calculate the number of rows needed

                # Display the figures in a grid
                for i in range(num_rows):
                    cols = st.columns(num_columns)  # Create a row of columns
                    for j in range(num_columns):
                        idx = i * num_columns + j
                        if idx < len(figures):
                            with cols[j]:
                                st.pyplot(figures[idx])


    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')

