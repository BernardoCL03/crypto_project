import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from dotenv import load_dotenv
import base64
import pyotp


dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

load_dotenv(dotenv_path=dotenv_path)

"""
#ESTAS FUNCIONES ESTAN COMENTADAS PORQUE SOLO SE UTILIZAN UNA SOLA VEZ PARA LA CREACION DE LA PUBLIC Y PRIVATE KEYS.

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
    print(type(pem))
    return pem

#-> PROCESO PARA CREACION Y ALMACENAMIENTO DE PP KEYS.

# obtenemos la private y public keys (class instances)
private_key, public_key = generate_rsa_keys()

# obtenemos nuestra clave secreta TOTP para generar OTP (one time passwords)
TOTP_SECRET = os.getenv("TOTP_SECRET")

# creamos el Totp en base a nuestra clave secreta
totp = pyotp.TOTP(TOTP_SECRET)
otp = totp.now().encode() # creamos las otps

# Serializar la clave privada usando el OTP
private_key_pem = serialize_private_key(private_key, password=TOTP_SECRET.encode())
public_key_pem = serialize_public_key(public_key)

public_key_pem_base64 = base64.b64encode(public_key_pem).decode('utf-8')
private_key_pem_base64 = base64.b64encode(private_key_pem).decode('utf-8')

# VISUALIZAMOS las pp keys para almacenarlas en el .env
print(public_key_pem_base64)
print('hola')
print(private_key_pem_base64)
"""

# Función para cifrar datos
def encrypt_data(public_key, data):
    if not isinstance(data, str):
        data = str(data)
    encrypted = public_key.encrypt(
        data.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode('utf-8')


# Función para descifrar datos
def decrypt_data(private_key, encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    original_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return original_data.decode('utf-8')

'''
Estas dos funciones se usarán para encriptar y desencriptar las imagenes
ya que, estos son strings muy largos y RSA no soporta strings tan largos
por lo que los dividimos por chunks y encriptamos cada chunk por separado
para al final unirlos, de igual manera para desencriptar lo hacemos por chunk.
'''

def encrypt_large_data(public_key, data, chunk_size=190):
    encrypted_chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        encrypted_chunk = public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode('utf-8'))
    return encrypted_chunks

def decrypt_large_data(private_key, encrypted_chunks):
    decrypted_data = b""
    for chunk in encrypted_chunks.split(','):
        decrypted_chunk = private_key.decrypt(
            base64.b64decode(chunk),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        decrypted_data += decrypted_chunk
    return decrypted_data

"""
-> PROCESO CARGAR PP KEYS Y ENCRIPTAR Y DESENCRIPTAR DATOS

public_key_base64 = os.getenv('PUBLIC_KEY')
private_key_base64 = os.getenv('PRIVATE_KEY')

# la serializamos (formato bytes)
public_key_pem = base64.b64decode(public_key_base64)
private_key_pem = base64.b64decode(private_key_base64)

TOTP_SECRET = os.getenv("TOTP_SECRET")
totp = pyotp.TOTP(TOTP_SECRET)
otp = totp.now().encode()
print(otp)

# aqui la deserializamos para convertirla en objeto y poder encriptar y desencriptar con esta
public_key = load_pem_public_key(public_key_pem)
private_key = load_pem_private_key(private_key_pem, password=TOTP_SECRET.encode())

encrypted_data = encrypt_data(public_key, "QUE CHINGUE A SU MADRE LIBRETICO")
print(encrypted_data)
decrypted_data = decrypt_data(private_key, encrypted_data)
print(decrypted_data)
"""
