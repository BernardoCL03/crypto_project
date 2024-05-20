import streamlit as st
from sqlalchemy import func
from back.model import Migrant
from back.database import SessionLocal
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def pie_chart_country(session):
    result = session.query(Migrant.country, func.count(Migrant.country)).group_by(Migrant.country).all()
    if result:
        data = pd.Series(dict(result), name="Cantidad por País")
        data.plot.pie(autopct="%.1f%%", ylabel='', startangle=90)
        st.pyplot(plt)
    else:
        st.write("No hay datos disponibles para los países.")

def bar_chart_gender(session):
    result = session.query(Migrant.gender, func.count(Migrant.gender)).group_by(Migrant.gender).all()
    if result:
        data = pd.DataFrame(result, columns=['Género', 'Cantidad'])
        data.plot(kind='bar', x='Género', y='Cantidad', legend=None)
        plt.xlabel('Género')
        plt.ylabel('Cantidad')
        plt.title('Distribución por Género')
        st.pyplot(plt)
    else:
        st.write("No hay datos disponibles para los géneros.")

def histogram_age(session):
    result = session.query(Migrant.age).all()
    if result:
        data = pd.DataFrame(result, columns=['Edad'])
        data.plot(kind='hist', bins=10, rwidth=0.8)
        plt.title('Distribución de Edades')
        plt.xlabel('Edad')
        plt.ylabel('Frecuencia')
        st.pyplot(plt)
    else:
        st.write("No hay datos disponibles para las edades.")

def line_chart_arrival_date(session):
    result = session.query(Migrant.arrival_date, func.count(Migrant.id)).group_by(Migrant.arrival_date).all()
    if result:
        data = pd.DataFrame(result, columns=['Fecha de Llegada', 'Cantidad'])
        data.plot(kind='line', x='Fecha de Llegada', y='Cantidad')
        plt.title('Tendencias de Llegada')
        plt.xlabel('Fecha de Llegada')
        plt.ylabel('Cantidad')
        st.pyplot(plt)
    else:
        st.write("No hay datos disponibles para las fechas de llegada.")

def pie_chart_page():
    st.title("Visualizaciones de Datos de Migrantes")
    with SessionLocal() as session:
        st.header("País de Origen")
        pie_chart_country(session)

        st.header("Distribución de Género")
        bar_chart_gender(session)

        st.header("Distribución de Edades")
        histogram_age(session)

        st.header("Tendencias de Llegadas")
        line_chart_arrival_date(session)

if __name__ == "__main__":
    pie_chart_page()
