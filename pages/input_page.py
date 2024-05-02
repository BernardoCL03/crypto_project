import streamlit as st
from back.model import SessionLocal, Migrant

def input_page():
    st.title("Ingresar Datos")
    with st.form(key='migrant_form'):
        name = st.text_input("Nombre")
        age = st.number_input("Edad", min_value=0)
        country = st.text_input("País de Origen")
        arrival_date = st.date_input("Fecha de Llegada")
        status = st.selectbox("Estado", options=['Pendiente', 'Aprobado', 'Denegado'])
        gender = st.radio("Género", options=['Masculino', 'Femenino', 'Otro'])
        phone = st.text_input("Número de Teléfono")
        submit_button = st.form_submit_button("Enviar Datos")

    if submit_button:
        with SessionLocal() as session:
            new_migrant = Migrant(
                name=name, age=age, country=country, arrival_date=arrival_date,
                status=status, gender=gender, phone=phone
            )
            session.add(new_migrant)
            session.commit()
            st.success("¡Datos ingresados exitosamente!")

if __name__ == "__main__":
    input_page()
