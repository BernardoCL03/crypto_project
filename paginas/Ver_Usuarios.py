import streamlit as st
import pandas as pd
from back.model import SessionLocal, User

def ver_usuarios_page():
    # Título para la sección de visualización
    st.title('Usuarios Registrados')

    # Crear una sesión para consultar la base de datos
    session = SessionLocal()

    if st.session_state.get('authenticated'):
        if st.session_state['user_type'] == 'Admin':
            try:
                # Obtener todos los usuarios
                users = session.query(User).all()
                if users:
                    # Preparar los datos para la tabla
                    user_data = [[user.id, user.username, user.user_type] for user in users]
                    # Crear un DataFrame con pandas y especificar los nombres de las columnas
                    df = pd.DataFrame(user_data, columns=['user_id', 'username', 'user_type'])
                    st.success("Usuarios registrados en el sistema:")
                    st.table(df)
                    
                    # Formulario para cambiar el nivel de acceso de un usuario
                    st.subheader("Cambiar Nivel de Acceso de Usuario")
                    usernames = {user.username: user.id for user in users}
                    selected_username = st.selectbox("Seleccione el nombre del usuario", options=list(usernames.keys()))
                    new_user_type = st.selectbox("Seleccione el nuevo nivel de acceso", options=["Admin", "User","Colaborador"])
                    
                    if st.button("Actualizar Nivel de Acceso"):
                        try:
                            user_to_update = session.query(User).filter(User.id == usernames[selected_username]).first()
                            if user_to_update:
                                user_to_update.user_type = new_user_type
                                session.commit()
                                st.success(f"El nivel de acceso del usuario '{selected_username}' ha sido actualizado a '{new_user_type}'.")
                                st.rerun()  # Reiniciar la página
                            else:
                                st.error("Usuario no encontrado.")
                        except Exception as e:
                            session.rollback()
                            st.error("Ocurrió un error al actualizar el nivel de acceso del usuario: " + str(e))
                    
                    # Formulario para dar de baja a un usuario
                    st.subheader("Dar de Baja a un Usuario")
                    selected_username_to_delete = st.selectbox("Seleccione el nombre del usuario a dar de baja", options=list(usernames.keys()), key="delete_user")
                    
                    if st.button("Dar de Baja"):
                        try:
                            user_to_delete = session.query(User).filter(User.id == usernames[selected_username_to_delete]).first()
                            if user_to_delete:
                                session.delete(user_to_delete)
                                session.commit()
                                st.success(f"El usuario '{selected_username_to_delete}' ha sido dado de baja del sistema.")
                                st.rerun()  # Reiniciar la página
                            else:
                                st.error("Usuario no encontrado.")
                        except Exception as e:
                            session.rollback()
                            st.error("Ocurrió un error al dar de baja al usuario: " + str(e))
                else:
                    st.write("No hay usuarios registrados.")
            except Exception as e:
                st.error("Ocurrió un error al recuperar los usuarios: " + str(e))
            finally:
                session.close()
    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')
