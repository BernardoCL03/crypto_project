import streamlit as st
from back.model import Migrant
from back.database import SessionLocal
import pandas as pd

def dataframe_page():
    st.title("Dataframe Visualization")
    # Use SessionLocal() context manager to handle the session lifecycle
    with SessionLocal() as session:
        # Query all data from the Migrant table
        result = session.query(Migrant).all()
        # Extract data into a list of dictionaries covering all model attributes
        data = [
            {
                "Name": migrant.name,
                "Age": migrant.age,
                "Country": migrant.country,
                "Arrival Date": migrant.arrival_date,
                "Status": migrant.status,
                "Gender": migrant.gender,
                "Phone": migrant.phone
            } for migrant in result
        ]
        # Convert list to DataFrame
        df = pd.DataFrame(data)
        # Display the DataFrame using Streamlit
        st.dataframe(df)

if __name__ == "__main__":
    dataframe_page()
