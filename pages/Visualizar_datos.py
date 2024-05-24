import streamlit as st


if st.session_state.get('authenticated'):
        if st.session_state['user_type'] == 'Admin' or st.session_state['user_type'] == 'User':
            st.title("Página de visualización de datos")
            st.warning("Work in progress")

else:
     st.error('Favor de iniciar sesión para acceder a esta página.')