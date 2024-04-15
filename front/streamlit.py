import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to add a new migrant's data
def add_migrant_data(name, age, country, arrival_date, status, gender, phone):
    new_data = {
        'Nombre': name,
        'Edad': age,
        'País de Origen': country,
        'Fecha de llegada': pd.to_datetime(arrival_date),
        'Estado': status,
        'Sexo': gender,
        'Teléfono': phone
    }
    # Append the new data to the existing DataFrame
    st.session_state.migrant_data = st.session_state.migrant_data.append(new_data, ignore_index=True)

# Initialize the session state with fake data if it's not already present
if 'migrant_data' not in st.session_state:
    fake_data = [
    {"Name": "Juan Perez", "Age": 30, "Country of Origin": "Guatemala", "Arrival Date": "2024-03-25", "Status": "Migrant", "Gender": "Male", "Phone": "1234567890"},
    {"Name": "Maria Lopez", "Age": 25, "Country of Origin": "El Salvador", "Arrival Date": "2024-03-20", "Status": "Refugee", "Gender": "Female", "Phone": "2345678901"},
    {"Name": "Carlos Hernández", "Age": 20, "Country of Origin": "Honduras", "Arrival Date": "2024-03-15", "Status": "Migrant", "Gender": "Male", "Phone": "3456789012"},
    {"Name": "Luisa Martínez", "Age": 35, "Country of Origin": "Mexico", "Arrival Date": "2024-03-10", "Status": "Refugee", "Gender": "Female", "Phone": "4567890123"},
    {"Name": "Roberto Gómez", "Age": 40, "Country of Origin": "Venezuela", "Arrival Date": "2024-03-05", "Status": "Migrant", "Gender": "Male", "Phone": "5678901234"},
    {"Name": "Sofia Castro", "Age": 28, "Country of Origin": "Colombia", "Arrival Date": "2024-02-28", "Status": "Refugee", "Gender": "Female", "Phone": "6789012345"},
    {"Name": "Gabriel Díaz", "Age": 33, "Country of Origin": "Peru", "Arrival Date": "2024-02-23", "Status": "Migrant", "Gender": "Male", "Phone": "7890123456"},
    {"Name": "Elena Torres", "Age": 22, "Country of Origin": "Bolivia", "Arrival Date": "2024-02-18", "Status": "Refugee", "Gender": "Female", "Phone": "8901234567"},
    {"Name": "Diego Rivera", "Age": 37, "Country of Origin": "Ecuador", "Arrival Date": "2024-02-13", "Status": "Migrant", "Gender": "Male", "Phone": "9012345678"},
    {"Name": "Ana Morales", "Age": 29, "Country of Origin": "Chile", "Arrival Date": "2024-02-08", "Status": "Refugee", "Gender": "Female", "Phone": "0123456789"}
]
    # Convert the 'Arrival Date' to datetime format right away
    for migrant in fake_data:
        migrant['Arrival Date'] = pd.to_datetime(migrant['Arrival Date'])
    # Initialize the session state with the fake data
    st.session_state['migrant_data'] = pd.DataFrame(fake_data)

# Page layout and form to add new migrants
st.title("Base de Datos Casa Monarca")

with st.form("migrant_info_form", clear_on_submit=True):
    st.write("### Información de nuevo Migrante")
    name = st.text_input("Nombre")
    age = st.number_input("Edad", min_value=0, max_value=120, step=1)
    country = st.text_input("País de Origen")
    arrival_date = st.date_input("Fecha de llegada")
    status = st.selectbox("Status", ["Migrante", "Refugiado"])
    gender = st.radio("Sexo", ["Masculino", "Femenino"])
    phone = st.text_input("Teléfono")
    submit_button = st.form_submit_button("Guardar")

    if submit_button:
        add_migrant_data(name, age, country, arrival_date, status, gender, phone)
        st.success("Información agregada exitosamente!")

# Display the current migrants
st.write("### Migrantes actuales")
st.dataframe(st.session_state['migrant_data'])

# Charts and analyses can now refer to st.session_state['migrant_data'] directly
# Section 3: Charts
st.write("### Estadísticas")
# Arrival over time
st.write("#### LLegadas con el tiempo")
if not st.session_state['migrant_data'].empty:
    arrivals_over_time = st.session_state['migrant_data']['Arrival Date'].value_counts().sort_index()
    plt.figure(figsize=(10, 4))
    plt.plot(arrivals_over_time.index, arrivals_over_time.values)
    plt.ylabel('Cantidad de llegadas')
    plt.xlabel('Fecha')
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # Pie chart of countries of origin
    st.write("#### Países de Origen")
    country_counts = st.session_state['migrant_data']['Country of Origin'].value_counts()
    plt.figure(figsize=(10, 8))
    plt.pie(country_counts, labels=country_counts.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(plt)
else:
    st.write("No data available for charts.")
    