import os
import streamlit as st
import base64
import pyotp
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# our decrypt data function
from back.encrypt import decrypt_data

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def admin_decrypt_page():
    encrypted_data_example = "u+D658or9d2OhIgHQodXsxKu9pNnQRahaW+IP9cY4XBGjJwZUbcj9DvrcnOuNXeZW0OjtDclkldB5T0+kShPTDtGBlRe47fspQLEPMcwvyslhvscir/QMlxxYidPYKgR9EMYvIDW/xCgfVFaOJgoMhv8IwMy1S4XoXb/kcaMpuSwh0oTB7MvJ85kAxcq0mJ7TSy6gnCsMMVfcuqvpDzYfRhfScJ7IAAr0rDgpdVClyT12HkE8CZ4Qw4vbtv9kzsyriCI2ou3/vLsS071dZxwXbC9rDpFkC57daLAtOE6wZDQ5ho3mZFF3vl9Y8oJKuSpGY5CDk5zsCzFfuP9PTptCg=="
    decrypted_data = decrypt_data(PRIVATE_KEY, encrypted_data_example)
    st.write("Datos desencriptados:", decrypted_data)
        

# Iniciamos la página
if __name__ == "__main__":
    st.title(':exclamation: Admin Decryption :exclamation:')
    if st.session_state.get('authenticated') and st.session_state['user_type'] == 'Admin':
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

        # cargamos variables de ambiente 
        dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
        load_dotenv(dotenv_path=dotenv_path)
        TOTP_SECRET = os.getenv("TOTP_SECRET")

        # leemos en formato base64, tenemos que convertirla a objeto valido
        private_key_base64 = os.getenv('PRIVATE_KEY')
        private_key_pem = base64.b64decode(private_key_base64)
        PRIVATE_KEY = load_pem_private_key(private_key_pem, password=TOTP_SECRET.encode())
        
        # Corremos la funcion para desencriptar
        admin_decrypt_page()

    elif st.session_state.get('authenticated') and st.session_state['user_type'] == 'User':
        st.error('No tienes permisos para acceder a esta página.')
    
    else:
        st.error('Favor de iniciar sesión.')
        