import pyotp
import qrcode
import streamlit as st

# Generar una clave secreta TOTP (esto se hace solo una vez y se almacena de manera segura)
totp_secret = pyotp.random_base32()
print(f"Guarda esta clave secreta de manera segura: {totp_secret}")

# Mostrar el código QR para configurar la aplicación autenticadora
otp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri("MigranteAdmin", issuer_name="Sistema de Gestión de Migrantes")
qr = qrcode.make(otp_uri)
qr.save("totp_qr.png")

# Mostrar la clave secreta y el código QR en Streamlit
st.write("Escanea este código QR con tu aplicación autenticadora TOTP (Google Authenticator, Authy, etc.)")
st.image("totp_qr.png")
st.write(f"Clave secreta (guárdala de manera segura): {totp_secret}")

# Guardar la clave secreta en un archivo para su uso posterior
with open("totp_secret.txt", "w") as f:
    f.write(totp_secret)
