import streamlit as st
import pandas as pd
from back.model import SessionLocal, Logs

def ver_logs():
    # Título para la sección de visualización
    st.title('Logs Registrados')

    # Crear una sesión para consultar la base de datos
    session = SessionLocal()

    if st.session_state.get('authenticated'):
        if st.session_state['user_type'] == 'Admin':
            st.markdown("""
                En esta página puedes consultar los registros de actividad en el sistema. Utiliza los filtros disponibles para encontrar información específica de manera eficiente.

                ### Funcionalidades:

                - **Filtrar por Username**: Puedes seleccionar un usuario específico para ver únicamente sus actividades registradas.
                - **Filtrar por Privilegios**: Filtra las actividades según los privilegios del usuario, como Admin, User o Colaborador.
                - **Filtrar por Acción**: Selecciona un tipo de acción específica para ver todas las instancias en las que se realizó esa acción.
                - **Filtrar por Rango de Fechas**: Selecciona un rango de fechas para ver las actividades registradas durante ese período.

                ### Cómo Usar los Filtros:

                1. Haz clic en el botón "Agregar filtro" para añadir un nuevo filtro.
                2. Selecciona la clave del filtro (Username, Privilegios, Acción, Timestamp).
                3. Dependiendo de la clave seleccionada, elige el valor específico o el rango de fechas.
                4. Repite los pasos anteriores para agregar múltiples filtros.
                5. Haz clic en el botón "Aplicar filtros" para ver los registros filtrados.

                > **Nota**: Puedes combinar múltiples filtros para obtener resultados más precisos. Por ejemplo, puedes filtrar por un usuario específico y un rango de fechas para ver sus actividades durante un período determinado.

                ### Importancia de los Logs:

                Los logs del sistema son fundamentales para monitorear la actividad, identificar problemas y garantizar la seguridad de la información. Utiliza esta herramienta para mantener un seguimiento detallado y preciso de todas las operaciones realizadas en el sistema.
            """)

            try:
                # Obtener todos los logs
                logs = session.query(Logs).all()
                if logs:
                    # Preparar los datos para la tabla
                    log_info = [[log.id, log.user_name, log.user_type, log.action, log.description, log.timestamp] for log in logs]
                    # Crear un DataFrame con pandas y especificar los nombres de las columnas
                    df = pd.DataFrame(log_info, columns=['Log_ID', 'Username', 'Privilegios', 'Acción', 'Descripción', 'Timestamp'])
                    variables = ['Username', 'Privilegios', 'Acción', 'Timestamp']
                    dictFilters = {column: list(df[column].unique()) for column in variables}

                    st.info('Filtros disponibles para los logs:')

                    if 'filters' not in st.session_state:
                        st.session_state['filters'] = []

                    # Limitar la adición de filtros duplicados
                    available_filters = [f for f in variables if f not in [list(d.keys())[0] for d in st.session_state['filters']]]

                    if available_filters:
                        if st.button("Agregar filtro"):
                            # Agregar un nuevo filtro solo si hay filtros disponibles
                            st.session_state['filters'].append({})

                    for i, filter_dict in enumerate(st.session_state['filters']):
                        col1, col2, col3 = st.columns([4, 4, 1])
                        if not filter_dict:
                            with col1:
                                key = st.selectbox(
                                    'Seleccione la clave del filtro:',
                                    options=available_filters,
                                    key=f'key_select_{i}'
                                )
                                st.session_state['filters'][i] = {key: None}
                                st.rerun()
                        else:
                            key = list(filter_dict.keys())[0]
                            with col1:
                                st.selectbox(
                                    'Seleccione la clave del filtro:',
                                    options=[key],
                                    key=f'key_fixed_{i}'
                                )
                            with col2:
                                if key == 'Timestamp':
                                    # Rango de fechas para Timestamp
                                    date_range = st.date_input(
                                        "Seleccione el rango de fechas:",
                                        value=(pd.to_datetime(df[key]).min().date(), pd.to_datetime(df[key]).max().date()),
                                        key=f'date_range_{i}'
                                    )
                                    st.session_state['filters'][i] = {key: date_range}
                                else:
                                    # Valores para los otros campos
                                    value = st.selectbox(
                                        'Seleccione el valor:',
                                        options=pd.unique(df[key].dropna()),
                                        key=f'value_select_{i}'
                                    )
                                    st.session_state['filters'][i] = {key: value}
                            with col3:
                                # Botón para eliminar el filtro
                                if st.button('x', key=f'remove_filter_{i}'):
                                    st.session_state['filters'].pop(i)
                                    st.rerun()

                    if st.session_state['filters']:
                        if st.button("Eliminar todos los filtros"):
                            st.session_state['filters'] = []
                            st.rerun()

                    # Aplicar filtros al DataFrame
                    if st.button("Aplicar filtros"):
                        df_filtered = df.copy()
                        for filter_dict in st.session_state['filters']:
                            for k, v in filter_dict.items():
                                if k == 'Timestamp':
                                    df_filtered['Date'] = pd.to_datetime(df_filtered[k]).dt.date
                                    df_filtered = df_filtered[(df_filtered['Date'] >= v[0]) & (df_filtered['Date'] <= v[1])]
                                    df_filtered.drop(columns=['Date'], inplace=True)
                                else:
                                    df_filtered = df_filtered[df_filtered[k] == v]

                        # Mostrar DataFrame filtrado
                        st.write(df_filtered)

            except Exception as e:
                st.error("Ocurrió un error al recuperar los logs: " + str(e))
            finally:
                session.close()

    # En teoría esto jamás se ve (ya que en menu.py se establece un filtro)
    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')

