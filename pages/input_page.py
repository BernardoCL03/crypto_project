
import streamlit as st
from back.model import SessionLocal, Migrant


def input_page():
    st.title("Input Data")
    with st.form(key='migrant_form'):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0)
        country = st.text_input("Country of Origin")
        arrival_date = st.date_input("Arrival Date")
        status = st.selectbox("Status", options=['Pending', 'Approved', 'Denied'])
        gender = st.radio("Gender", options=['Male', 'Female', 'Other'])
        phone = st.text_input("Phone Number")
        submit_button = st.form_submit_button("Submit Data")

    if submit_button:
        with SessionLocal() as session:
            new_migrant = Migrant(
                name=name, age=age, country=country, arrival_date=arrival_date,
                status=status, gender=gender, phone=phone
            )
            session.add(new_migrant)
            session.commit()
            st.success("Data submitted successfully!")

if __name__ == "__main__":
    input_page()
