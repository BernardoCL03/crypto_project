import streamlit as st
from back.model import Migrant
from back.database import SessionLocal
import pandas as pd

def dataframe_page():
    st.title("Visualización de Datos")
    # Use SessionLocal() context manager to handle the session lifecycle
    with SessionLocal() as session:
        # Query all data from the Migrant table
        result = session.query(Migrant).all()
        # Extract data into a list of dictionaries covering all model attributes
        data = [
            {
                "Nombre": migrant.name,
                "Edad": migrant.age,
                "País": migrant.country,
                "Fecha de Llegada": migrant.arrival_date,
                "Estado": migrant.status,
                "Género": migrant.gender,
                "Teléfono": migrant.phone
            } for migrant in result
        ]
        # Convert list to DataFrame
        df = pd.DataFrame(data)
        # Display the DataFrame using Streamlit
        st.dataframe(df)

if __name__ == "__main__":
    dataframe_page()
