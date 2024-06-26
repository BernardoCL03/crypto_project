from back.model import SessionLocal, User, Logs
from sqlalchemy.exc import IntegrityError
import streamlit as st
import re

#st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def creacion_de_usuarios_page():

    st.title('Página de creación de usuarios :bust_in_silhouette: :white_check_mark:')

    if st.session_state.get('authenticated'): # authenticated es True si el usuario ya se autentico, y False, si no.
        # solamente los admins tienen derecho a crear otros usuarios
        if st.session_state['user_type'] == 'Admin':
            with st.container():
                st.success("Página de creación de usuarios")
                
                st.markdown(f"""
                ¡Bienvenido, <b>{st.session_state['username']}!</b> En este apartado podrás crear usuarios con los permisos que desees (Colaborador, Usuario o Admin). Es necesario:
                <ul style='list-style-type:none;'>
                    <li><b>Nombre de usuario:</b></li>
                        <ul style='list-style-type:none; margin-left: 20px;'>  <!-- Ahi se anade el margen a la izquierda para la indentacion -->
                            <li>El nombre de usuario únicamente puede contener letras, números, puntos y guíones bajos.</li>
                        </ul>
                    <li><b>Contraseña:</b></li>
                        <ul style='list-style-type:none; margin-left: 20px;'> 
                            <li>Debe contener al menos 8 caracteres</li>
                            <li>Debe contener al menos 1 letra mayúscula</li>
                            <li>Debe contener al menos 1 símbolo (no alfanumérico)</li>
                        </ul>
                    <li><b>Permisos (Colaborador por default)</b></li>
                </ul>
                """, unsafe_allow_html=True)

                username = st.text_input("Nombre de usuario")
                password = st.text_input("Contraseña", type="password")
                privileges = st.radio("Privilegios", options=['Colaborador','User', 'Admin'])

            # Contraseña de mínimo 8 de longitus, con mayúscula y un signo
            def validate_password(password):
                    if len(password) < 8:
                        return "La contraseña debe tener al menos 8 caracteres."
                    if not re.search(r"[A-Z]", password):
                        return "La contraseña debe tener al menos una letra mayúscula."
                    if not re.search(r"\W", password):
                        return "La contraseña debe tener al menos un símbolo."
                    return None

            def validate_username(username):
                if not re.match(r"^[a-zA-Z0-9._]+$", username):
                    return "El nombre de usuario solo puede contener letras, números, puntos y guiones bajos."
                return None

            if st.button('Crear Usuario'):
                password_error = validate_password(password) 
                username_error = validate_username(username)

                # Checar que usuario y contrasena sean validos
                if username_error or password_error: 
                    if username_error:
                        st.error(username_error)
                    if password_error:
                        st.error(password_error)

                # Si ambos son validos 
                else:
                    session = SessionLocal()
                    try:
                        # Verificar si el nombre de usuario ya existe
                        if session.query(User).filter(User.username == username).first():
                            st.error("El nombre de usuario ya existe. Por favor, elige otro.")
                        else:
                            # Crear el nuevo usuario
                            new_user = User(username=username, user_type=privileges)
                            new_user.set_password(password)  # Hasheamos la contraseña y así la almacenamos
                            session.add(new_user)

                            # Registramos en los logs la creacion del usuario
                            log_entry = Logs(
                                action="User Management",
                                user_name=st.session_state['username'],  # Nombre de usuario del admin que crea el usuario
                                user_type=st.session_state['user_type'], # Los permisos de usuario (admin unicamente)
                                description=f"Usuario '{st.session_state['username']}' con ID '{st.session_state['id']}' creó  usuario '{username}' con permisos de '{privileges}'" # descripcion de lo sucedido
                            )
                            session.add(log_entry)
                            session.commit()
                            st.success("Usuario creado con éxito.")
                    except IntegrityError:
                        st.error("Hubo un problema al crear el usuario. Por favor, inténtalo de nuevo.")
                        session.rollback()  # Rollback en caso de error de integridad
                    finally:
                        session.close()

        if st.session_state['user_type'] == 'User':
            st.error(f"¡Lo sentimos {st.session_state['username']}! Solamente usuarios con permisos de Admin tienen derecho a utilizar esta página.")
    else:
        st.error("Favor de iniciar sesión para acceder a esta página.")
