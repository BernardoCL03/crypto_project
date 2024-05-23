import os
import streamlit as st
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from back.model import SessionLocal, Health, Education, Transit, General # table names
from back.encrypt import encrypt_data
from dotenv import load_dotenv


st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def input_page():
    st.title("Ingresar Datos")
    with (st.form(key='migrant_form')):
        arrival_date = st.date_input("Fecha de Llegada")
        type = st.selectbox('Tipo de registro', options=['Adulto', 'Niña acompañada', 'Niño acompañado', 'Adolescente acompañado', 'Niña no acompañada', 'Niño no acompañado', 'Adolescente no acompañado'])
        name = st.text_input("Nombre")
        last_name = st.text_input("Apellidos")
        gender = st.radio("Sexo", options=['Mujer LGBTTTIQ+', 'Mujer', 'Hombre  LGBTTTIQ+', 'Hombre'])
        birth_date = st.date_input("Fecha de nacimiento", min_value=min_date, max_value=today, value=today)
        age = st.number_input("Edad", min_value=0)
        country_of_origin = st.selectbox("País de Origen", options=['Mexico', 'USA', 'Guatemala', 'Honduras', 'El Salvador', 'Venezuela', 'Nicaragua', 'Haiti', 'Colombia', 'Cuba', 'Argentina', 'Afganistan', 'Siria', 'Alemania', 'Brasil', 'Peru', 'Guyana Francesa', 'Belice', 'Panama', 'Ecuador'])
        civil_status = st.selectbox("Estado Civil", options=['Casad@', 'Divorciad@', 'Solter@', 'Separad@', 'Viud@', 'Unión libre'])
        has_children = st.radio("Hijos", options=['Si', 'No'])
        children_traveling = st.number_input("¿Cuántos hijos están viajando con usted?", min_value=0) if has_children == 'Si' else 0
        can_read_write = st.radio("Puede Leer y Escribir", options=['Sí', 'No'])
        last_grade_study = st.selectbox("Último Grado de Estudio", options=['Preescolar', 'Primaria', 'Secundaria', 'Bachillerato', 'Bachillerato Técnico', 'Universidad', 'No Escolarizado'])
        # TODO: fix languages to appear in db
        languages_spoken = st.multiselect("Idiomas que Habla", options=['Inglés', 'Español', 'Francés', 'Criollo Haitiano', 'Garífuna', 'Otro'])
        other_language = st.text_input("Si habla otro idioma, especifique")
        if 'Otro' not in languages_spoken:
            other_language = 'NA'
        date_left_origin = st.date_input("Fecha en que Dejó el País de Origen", max_value=today, value=today)
        traveling_alone_accompanied = st.radio("Viajando Solo o Acompañado", options=['Solo', 'Acompañado'], index=1)
        who_accompanied = st.radio("¿Por quién está siendo acompañado/a?", # TODO fix potential bug, algunas veces aparece, otras veces no...
                                   options=[
                                       'Hijo/a', 'Pareja', 'Pareja e hijo/a', 'Mamá', 'Papá', 'Mamá y papá','Primo/a','Amigo/a',
                                       'Otro pariente']) if traveling_alone_accompanied == 'Acompañado' else 'NA'
        which_relative = st.text_input("¿Por cuál pariente salió acompañado?")
        if who_accompanied != 'Otro pariente':
            which_relative = 'NA'
        how_traveled = st.text_input("¿Cómo viajó?")
        reason_for_leaving = st.text_input("¿Por qué razón tomó la decisión de salir de su país?")
        abuse_during_travel = st.radio("Durante su viaje desde que salió de su país hasta antes de llegar a México, ¿Usted sufrió de algún abuso a sus Derechos Humanos?", options=['Sí', 'No'])
        type_of_abuse = st.text_input("¿Qué tipo de abuso vivió?", placeholder="Golpes, Secuestro, Extorsión, Violación, etc.") if abuse_during_travel == 'Sí' else 'NA'
        abuse_in_mexico = st.radio("Cuando usted entró a territorio mexicano, ¿Usted vivió algún abuso o agresión?", options=['Sí', 'No'])
        type_of_abuse_mexico = st.text_input("¿Qué tipo de abuso o agresión vivió?") if abuse_in_mexico == 'Sí' else 'NA'
        abuser = st.text_input("¿Quién le ocasionó el abuso o la agresión?") if abuse_in_mexico == 'Sí' else 'NA'
        paid_guide = st.radio("En algún momento de su camino, ¿Usted le pagó a algún guía para viajar?", options=['Sí', 'No'])
        amount_paid = st.radio("¿Cuánto dinero pagó?",
                               options=[
                                   'Menos de 20,000 MX ($1,000 US)',
                                   '20,000 a 60,000 MX ($1,000 a 3,000 US)',
                                   '61,000 a 100,000 MX ($3,000 a 5,000 US)',
                                   'Más de 100,000 MX ($5,000 US)'
                               ]) if paid_guide == 'Sí' else 'NA'
        date_entered_mexico = st.date_input("Fecha en que ingresó a México")
        entry_point_mexico = st.radio("¿Por dónde ingresó a México?",
                                      options=[
                                          'Tapachula',
                                          'Tenosique',
                                          'Chetumal',
                                          'Palenque',
                                          'Matamoros',
                                          'Reynosa',
                                          'Veracruz',
                                          'Tabasco',
                                      ])
        final_destination = st.radio("¿Cuál es su destino final?",options=['México','Estados Unidos','Regresar a mi país de origen'])
        destination_monterrey = st.radio("Si se queda en México, ¿Su destino es Monterrey?",options=['Sí', 'No']) if final_destination == 'México' else 'NA'
        reason_stay_monterrey = st.text_input("¿Por qué pensaría quedarse en Monterrey?") if destination_monterrey == 'Sí' else 'NA'
        support_network_monterrey = st.radio(
            "¿Cuenta con una red de apoyo en Monterrey? Conocidos, amigos, familiares, etc.", options=['Sí', 'No'])
        time_knowing_support = st.text_input("Tiempo de conocer a su red de apoyo") if support_network_monterrey == 'Sí' else 'NA'
        tried_enter_us = st.radio("¿Usted ha intentado ingresar a Estados Unidos?",options=['Sí', 'No'])
        support_network_us = st.radio(
            "¿Usted cuenta con una red de apoyo en Estados Unidos?",
            options=['Sí', 'No']
        )
        description_support_us = st.text_input("Descripción de la red de apoyo con la que cuenta en Estados Unidos") if support_network_us == 'Sí' else 'NA'
        been_in_migration_station = st.radio("¿Usted ha estado en alguna estación migratoria?",options=['Sí', 'No'])
        suffered_aggression = st.radio("¿Sufrió o vivió situaciones donde se sintió agredido por autoridades en las estaciones migratorias?",options=['Sí', 'No']) if been_in_migration_station == 'Sí' else 'NA'
        migration_station_location = st.text_input("¿En cuál Estado y/o País estuvo en una estación migratoria?") if been_in_migration_station == 'Sí' else 'NA'
        description_of_facts = st.text_area("Descripción de los hechos.") if been_in_migration_station == 'Sí' else 'NA'
        filed_complaint = st.radio("Ante las vivencias de abuso de autoridad, agresiones y vulnerabilidad a Derechos Humanos, ¿Usted interpuso una denuncia formal?",
                                   options=['Sí', 'No'], index=1
                                   ) if been_in_migration_station == 'Sí' else 'NA'
        reason_no_complaint = st.text_input("¿Por qué razón no lo hizo?") if filed_complaint == 'No' else 'NA'
        solution_offered = st.text_input("¿Qué solución le brindaron?") if filed_complaint == 'Sí' else 'NA'
        can_return_to_country = st.radio("¿Usted puede regresar a su país?",options=['Sí', 'No'], index=1)
        reason_cannot_return = st.text_input("¿Por qué razón no puede regresar a su país?") if can_return_to_country == 'No' else 'NA'
        has_illness = st.radio("¿Actualmente usted padece alguna enfermedad?",options=['Sí', 'No'])
        illness_details = st.text_input("¿Cuál enfermedad padece?") if has_illness == 'Sí' else 'NA'
        on_medical_treatment = st.radio("¿Se encuentra o encontraba en algún tratamiento médico?",options=['Sí', 'No'])
        medical_treatment_description = st.text_input("Descripción del tratamiento médico que está recibiendo o que estuvo recibiendo, razón de por qué lo abandonó, etc.") if on_medical_treatment == 'Sí' else 'NA'
        has_allergy = st.radio("¿Usted padece algún tipo de alergia?",options=['Sí', 'No'])
        allergy_details = st.text_input("Tipo de alergia o a qué es alérgico/a") if has_allergy == 'Sí' else 'NA'
        is_pregnant = st.radio("¿Actualmente usted está embarazada?",options=['Sí', 'No', 'NA'])
        months_pregnant = st.radio("¿Cuántos meses de embarazo tiene?", options=['1 mes', '2 meses', '3 meses', '4 meses', '5 meses', '6 meses', '7 meses', '8 meses', '9 meses', 'NA'],) if is_pregnant == 'Sí' else 'NA'
        has_prenatal_care = st.radio("¿Cuenta con control prenatal?",options=['Sí', 'No']) if is_pregnant == 'Sí' else 'NA'
        stayed_in_shelter = st.radio("En su trayecto por México, ¿Usted se ha estado en algún otro albergue?",options=['Sí', 'No'])
        last_shelter = st.text_input("¿Cuál fue el último albergue en el que estuvo?")
        access_to_casa_monarca = st.radio("¿Se le brindó acceso al albergue de Casa Monarca?",options=['Sí', 'No'], index=1)
        reason_for_denial = st.text_input("¿Por qué se le negó el acceso al albergue?") if access_to_casa_monarca == 'No' else 'NA'
        services_provided = st.multiselect(
            "¿Cuáles servicios se le brindaron a la persona?",
            options=[
                'Agua y alimento',
                'Kit de higiene',
                'Ropa y calzado',
                'Acceso a higiene (Regadera)',
                'Asesoría legal',
                'Orientación legal',
                'Orientación en búsqueda de empleo',
                'Orientación en el acceso a la educación',
                'Orientación en la búsqueda de vivienda',
                'Orientación para acceder a servicios de salud',
                'Orientación a servicios prisológicos',
                'Canalización a servicios prisológicos',
                'Atención psicosocial'
            ]
        )
        assigned_dormitory = st.radio(
            "Dormitorio en el cual se asignó",
            options=[
                'Dormitorio de caballeros planta baja',
                'Dormitorio de caballeros planta alta',
                'Dormitorio de damas planta baja',
                'Dormitorio de damas planta alta',
                'Dormitorio de la comunidad LGBTTIQ+',
                'Dormitorio de familia'
            ]
        ) if access_to_casa_monarca == 'Sí' else 'NA'
        distinctive_signs = st.text_area("Señas particulares.")
        emergency_contact = st.text_input("Contacto de emergencia")
        emergency_contact_location = st.text_input("Geográficamente, ¿Dónde se encuentra su contacto de emergencia? País, Estado, Ciudad, Departamento, Comunidad, etc.")
        final_observations = st.text_area("Observaciones finales.")
        submit_button = st.form_submit_button("Encriptar datos y subir a la base de datos.")

    if submit_button:
        with SessionLocal() as session:
            # First, create and add the general record
            new_general = General(
                arrival_date=encrypt_data(PUBLIC_KEY, arrival_date),
                type=encrypt_data(PUBLIC_KEY, type),
                name=encrypt_data(PUBLIC_KEY, name),
                last_name=encrypt_data(PUBLIC_KEY, last_name),
                gender=encrypt_data(PUBLIC_KEY, gender),
                birth_date=encrypt_data(PUBLIC_KEY, birth_date),  # Convertimos la fecha a string para encriptarla
                age=encrypt_data(PUBLIC_KEY, str(age)),  # Convertimos el número a string para encriptar
                country_of_origin=encrypt_data(PUBLIC_KEY, country_of_origin),
                civil_status=encrypt_data(PUBLIC_KEY, civil_status),
                has_children=encrypt_data(PUBLIC_KEY, str(has_children)),  # Convertimos el booleano a string para encriptar
                children_traveling=encrypt_data(PUBLIC_KEY, str(children_traveling)),  # Convertimos el número a string para encriptar
                can_return_to_country=encrypt_data(PUBLIC_KEY, str(can_return_to_country)),  # Convertimos el booleano a string para encriptar
                reason_cannot_return=encrypt_data(PUBLIC_KEY, reason_cannot_return),
                access_to_casa_monarca=encrypt_data(PUBLIC_KEY, str(access_to_casa_monarca)),  # Convertimos el booleano a string para encriptar
                reason_for_denial=encrypt_data(PUBLIC_KEY, reason_for_denial),
                services_provided=encrypt_data(PUBLIC_KEY, ', '.join(services_provided)),  # Concatenamos y encriptamos
                assigned_dormitory=encrypt_data(PUBLIC_KEY, assigned_dormitory),
                distinctive_signs=encrypt_data(PUBLIC_KEY, distinctive_signs),
                emergency_contact=encrypt_data(PUBLIC_KEY, emergency_contact),
                emergency_contact_location=encrypt_data(PUBLIC_KEY, emergency_contact_location),
                final_observations=encrypt_data(PUBLIC_KEY, final_observations)
            )
            session.add(new_general)
            session.commit()  # Commit to get the ID
    
            # Use the ID from the general record for related tables
            new_education = Education(
                id=new_general.id, can_read_write=can_read_write, last_grade_study=last_grade_study,
                languages_spoken=(','.join(languages_spoken)), other_language=other_language
            )
            new_health = Health(
                id=new_general.id, has_illness=has_illness, illness_details=illness_details,
                on_medical_treatment=on_medical_treatment, medical_treatment_description=medical_treatment_description,
                has_allergy=has_allergy, allergy_details=allergy_details, is_pregnant=is_pregnant,
                months_pregnant=months_pregnant, has_prenatal_care=has_prenatal_care
            )
            new_transit = Transit(
                id=new_general.id, date_left_origin=date_left_origin, traveling_alone_accompanied=traveling_alone_accompanied,
                who_accompanied=who_accompanied, which_relative=which_relative, how_traveled=how_traveled,
                reason_for_leaving=reason_for_leaving, abuse_during_travel=abuse_during_travel, type_of_abuse=type_of_abuse,
                abuse_in_mexico=abuse_in_mexico, type_of_abuse_mexico=type_of_abuse_mexico, abuser=abuser,
                paid_guide=paid_guide, amount_paid=amount_paid, date_entered_mexico=date_entered_mexico,
                entry_point_mexico=entry_point_mexico, final_destination=final_destination,
                destination_monterrey=destination_monterrey, reason_stay_monterrey=reason_stay_monterrey,
                support_network_monterrey=support_network_monterrey, time_knowing_support=time_knowing_support,
                tried_enter_us=tried_enter_us, support_network_us=support_network_us,
                description_support_us=description_support_us, been_in_migration_station=been_in_migration_station,
                suffered_aggression=suffered_aggression, migration_station_location=migration_station_location,
                description_of_facts=description_of_facts, filed_complaint=filed_complaint,
                reason_no_complaint=reason_no_complaint, solution_offered=solution_offered,
                stayed_in_shelter=stayed_in_shelter, last_shelter=last_shelter
            )
    
            # Add the records for related tables
            session.add(new_education)
            session.add(new_health)
            session.add(new_transit)
    
            # Commit all changes
            session.commit()

            st.success("¡Datos ingresados exitosamente!")


if __name__ == "__main__":
    st.title('Registro de migrantes :bust_in_silhouette:')
    today = datetime.today()
    min_date = today - timedelta(days=365.25 * 100)
    if st.session_state.get('authenticated'):
        if st.session_state['user_type'] == 'Admin' or st.session_state['user_type'] == 'User':
            # cargamos .env
            dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
            load_dotenv(dotenv_path=dotenv_path)

            # leemos en formato base64, tenemos que convertirla a objeto valido
            public_key_base64 = os.getenv('PUBLIC_KEY')
            public_key_pem = base64.b64decode(public_key_base64)
            PUBLIC_KEY = load_pem_public_key(public_key_pem)

            input_page()
    else:
        st.error('Favor de iniciar sesión para acceder a esta página.')
