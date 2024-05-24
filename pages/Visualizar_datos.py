import streamlit as st

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

if st.session_state.get('authenticated'):
    st.sidebar.write(f"Usuario: {st.session_state['username']}")
    st.sidebar.write(f"Permisos: {st.session_state['user_type']}")
    if st.sidebar.button("Cerrar sesión"):
        # Al hacer clic en cerrar sesión, cambiamos el estado a no autenticado
        st.session_state.authenticated = False

st.title("Página de visualización de datos")

if st.session_state.get('authenticated'):
        if st.session_state['user_type'] == 'Admin' or st.session_state['user_type'] == 'User':
            st.warning("Work in progress")

else:
     st.error('Favor de iniciar sesión para acceder a esta página.')