import streamlit as st
from sqlalchemy import func  # Correctly import func from sqlalchemy
from back.model import Migrant
from back.database import SessionLocal
import pandas as pd
import matplotlib.pyplot as plt

def pie_chart_page():
    st.title("Pie Chart of Countries of Origin")
    # Create a session and perform a query
    with SessionLocal() as session:
        # Adjusted to use the correct attribute 'country' from your Migrant model
        result = session.query(Migrant.country, func.count(Migrant.country)).group_by(Migrant.country).all()
        if result:
            # Convert query result to a Series
            data = pd.Series(dict(result), name="Count by Country")
            # Plotting the pie chart
            data.plot.pie(autopct="%.1f%%", ylabel='', startangle=90)
            st.pyplot(plt)
        else:
            st.write("No data available to display.")

if __name__ == "__main__":
    pie_chart_page()
