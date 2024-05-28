import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from back.model import SessionLocal, General, Transit, Health, Education
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

# función para desencriptar todos los dataos guardados en la base de datos
def admin_decrypt_page(private_key):
    with SessionLocal() as session:
        general_query = session.query(General).all()
        transit_query = {transit.id: transit for transit in session.query(Transit).all()}
        health_query = {health.id: health for health in session.query(Health).all()}
        education_query = {education.id: education for education in session.query(Education).all()}

        data = []
        for migrant in general_query:
            transit = transit_query.get(migrant.id, {})
            health = health_query.get(migrant.id, {})
            education = education_query.get(migrant.id, {})
            
            decrypted_migrant = {
                'id': migrant.id,
                'arrival_date': decrypt_data(private_key, migrant.arrival_date),
                'type': decrypt_data(private_key, migrant.type),
                'name': decrypt_data(private_key, migrant.name),
                'last_name': decrypt_data(private_key, migrant.last_name),
                'gender': decrypt_data(private_key, migrant.gender),
                'birth_date': decrypt_data(private_key, migrant.birth_date),
                'age': decrypt_data(private_key, migrant.age),
                'country_of_origin': decrypt_data(private_key, migrant.country_of_origin),
                'civil_status': decrypt_data(private_key, migrant.civil_status),
                'has_children': decrypt_data(private_key, migrant.has_children),
                'children_traveling': decrypt_data(private_key, migrant.children_traveling),
                'can_return_to_country': decrypt_data(private_key, migrant.can_return_to_country),
                'reason_cannot_return': decrypt_data(private_key, migrant.reason_cannot_return),
                'access_to_casa_monarca': decrypt_data(private_key, migrant.access_to_casa_monarca),
                'reason_for_denial': decrypt_data(private_key, migrant.reason_for_denial),
                'services_provided': decrypt_data(private_key, migrant.services_provided),
                'assigned_dormitory': decrypt_data(private_key, migrant.assigned_dormitory),
                'distinctive_signs': decrypt_data(private_key, migrant.distinctive_signs),
                'emergency_contact': decrypt_data(private_key, migrant.emergency_contact),
                'emergency_contact_location': decrypt_data(private_key, migrant.emergency_contact_location),
                'final_observations': decrypt_data(private_key, migrant.final_observations),
                'front_photo': decrypt_large_data(private_key, migrant.front_photo) if migrant.front_photo else None,
                'right_profile_photo': decrypt_large_data(private_key, migrant.right_profile_photo) if migrant.right_profile_photo else None,
                'left_profile_photo': decrypt_large_data(private_key, migrant.left_profile_photo) if migrant.left_profile_photo else None,
                'transit': {
                    'date_left_origin': decrypt_data(private_key, transit.date_left_origin),
                    'traveling_alone_accompanied': decrypt_data(private_key, transit.traveling_alone_accompanied),
                    'who_accompanied': decrypt_data(private_key, transit.who_accompanied),
                    'which_relative': decrypt_data(private_key, transit.which_relative),
                    'how_traveled': decrypt_data(private_key, transit.how_traveled),
                    'reason_for_leaving': decrypt_data(private_key, transit.reason_for_leaving),
                    'abuse_during_travel': decrypt_data(private_key, transit.abuse_during_travel),
                    'type_of_abuse': decrypt_data(private_key, transit.type_of_abuse),
                    'abuse_in_mexico': decrypt_data(private_key, transit.abuse_in_mexico),
                    'type_of_abuse_mexico': decrypt_data(private_key, transit.type_of_abuse_mexico),
                    'abuser': decrypt_data(private_key, transit.abuser),
                    'paid_guide': decrypt_data(private_key, transit.paid_guide),
                    'amount_paid': decrypt_data(private_key, transit.amount_paid),
                    'date_entered_mexico': decrypt_data(private_key, transit.date_entered_mexico),
                    'entry_point_mexico': decrypt_data(private_key, transit.entry_point_mexico),
                    'final_destination': decrypt_data(private_key, transit.final_destination),
                    'destination_monterrey': decrypt_data(private_key, transit.destination_monterrey),
                    'reason_stay_monterrey': decrypt_data(private_key, transit.reason_stay_monterrey),
                    'support_network_monterrey': decrypt_data(private_key, transit.support_network_monterrey),
                    'time_knowing_support': decrypt_data(private_key, transit.time_knowing_support),
                    'tried_enter_us': decrypt_data(private_key, transit.tried_enter_us),
                    'support_network_us': decrypt_data(private_key, transit.support_network_us),
                    'description_support_us': decrypt_data(private_key, transit.description_support_us),
                    'been_in_migration_station': decrypt_data(private_key, transit.been_in_migration_station),
                    'suffered_aggression': decrypt_data(private_key, transit.suffered_aggression),
                    'migration_station_location': decrypt_data(private_key, transit.migration_station_location),
                    'description_of_facts': decrypt_data(private_key, transit.description_of_facts),
                    'filed_complaint': decrypt_data(private_key, transit.filed_complaint),
                    'reason_no_complaint': decrypt_data(private_key, transit.reason_no_complaint),
                    'solution_offered': decrypt_data(private_key, transit.solution_offered),
                    'stayed_in_shelter': decrypt_data(private_key, transit.stayed_in_shelter),
                    'last_shelter': decrypt_data(private_key, transit.last_shelter),
                },
                'health': {
                    'has_illness': decrypt_data(private_key, health.has_illness),
                    'illness_details': decrypt_data(private_key, health.illness_details),
                    'on_medical_treatment': decrypt_data(private_key, health.on_medical_treatment),
                    'medical_treatment_description': decrypt_data(private_key, health.medical_treatment_description),
                    'has_allergy': decrypt_data(private_key, health.has_allergy),
                    'allergy_details': decrypt_data(private_key, health.allergy_details),
                    'is_pregnant': decrypt_data(private_key, health.is_pregnant),
                    'months_pregnant': decrypt_data(private_key, health.months_pregnant),
                    'has_prenatal_care': decrypt_data(private_key, health.has_prenatal_care),
                },
                'education': {
                    'can_read_write': decrypt_data(private_key, education.can_read_write),
                    'last_grade_study': decrypt_data(private_key, education.last_grade_study),
                    'languages_spoken': decrypt_data(private_key, education.languages_spoken),
                    'other_language': decrypt_data(private_key, education.other_language),
                }
            }
            data.append(decrypted_migrant)

        return data

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
