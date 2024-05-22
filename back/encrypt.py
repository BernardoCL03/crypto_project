import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv
import pyotp


dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

load_dotenv(dotenv_path=dotenv_path)

# genera la clave publica y privada. 
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

# esta nos serializa la clave publica para poderla guardar en el .env, ya que si no se serializa,
# la clave es solamente un objeto de una clase, de esta manera, obtenemos el string
def serialize_public_key(public_key) -> str:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

# esta hace lo mismo para la private key, pero ademas necesitamos una contraseña TOTP para agregar una capa extra de protección.
# ya que al serializar la private key, nos permite visualizarla, y estamos agregando esta capa extra de protección del TOTP
def serialize_private_key(private_key, password):
    encryption_algorithm = serialization.BestAvailableEncryption(password)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    return pem

# obtenemos la private y public keys (class instances)
private_key, public_key = generate_rsa_keys()

# obtenemos nuestra clave secreta TOTP para generar OTP (one time passwords)
TOTP_SECRET = os.getenv("TOTP_SECRET")

# creamos el Totp en base a nuestra clave secreta
totp = pyotp.TOTP(TOTP_SECRET)
otp = totp.now().encode() # creamos las otps
print(otp)

# Serializar la clave privada usando el OTP
private_key_pem = serialize_private_key(private_key, password=otp)
public_key_pem = serialize_public_key(public_key)

print(private_key_pem)
print(public_key_pem)