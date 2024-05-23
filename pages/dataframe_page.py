import streamlit as st
from back.model import Education, Health, Transit
from back.model import SessionLocal
import pandas as pd

st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

def dataframe_page():
    st.title("Visualización de Datos de Educacion")
    # Use SessionLocal() context manager to handle the session lifecycle
    with SessionLocal() as session:
        # Query all data from the Education table
        result = session.query(Education).all()
        # Extract data into a list of dictionaries covering all model attributes
        data = [
            {
                "Id": education.id,
                "Can Read and Write": education.can_read_write,
                "Last Grade Studied": education.last_grade_study,
                "Languages Spoken": education.languages_spoken,
                "Other Language": education.other_language
            } for education in result
        ]
        # Convert list to DataFrame
        df = pd.DataFrame(data)
        # Display the DataFrame using Streamlit
        st.dataframe(df)

        # ---------------
        st.title("Visualización de Datos de Salud")
        result1 = session.query(Health).all()
    # Extract data into a list of dictionaries covering all model attributes
        data1 = [
        {
            "Id": health.id,
            "Has Illness": health.has_illness,
            "Illness Details": health.illness_details,
            "On Medical Treatment": health.on_medical_treatment,
            "Medical Treatment Description": health.medical_treatment_description,
            "Has Allergy": health.has_allergy,
            "Allergy Details": health.allergy_details,
            "Is Pregnant": health.is_pregnant,
            "Months Pregnant": health.months_pregnant,
            "Has Prenatal Care": health.has_prenatal_care
        } for health in result1
    ]
    # Convert list to DataFrame
        df1 = pd.DataFrame(data1)
        # Display the DataFrame using Streamlit
        st.dataframe(df1)
        st.title("Visualización de Datos de Tránsito")
        result2 = session.query(Transit).all()
        # Extract data into a list of dictionaries covering all model attributes
        data2 = [
            {
                "Id": transit.id,
                "Date Left Origin": transit.date_left_origin,
                "Traveling Alone or Accompanied": transit.traveling_alone_accompanied,
                "Who Accompanied": transit.who_accompanied,
                "Which Relative": transit.which_relative,
                "How Traveled": transit.how_traveled,
                "Reason for Leaving": transit.reason_for_leaving,
                "Abuse During Travel": transit.abuse_during_travel,
                "Type of Abuse": transit.type_of_abuse,
                "Abuse in Mexico": transit.abuse_in_mexico,
                "Type of Abuse in Mexico": transit.type_of_abuse_mexico,
                "Abuser": transit.abuser,
                "Paid Guide": transit.paid_guide,
                "Amount Paid": transit.amount_paid,
                "Date Entered Mexico": transit.date_entered_mexico,
                "Entry Point Mexico": transit.entry_point_mexico,
                "Final Destination": transit.final_destination,
                "Destination Monterrey": transit.destination_monterrey,
                "Reason Stay Monterrey": transit.reason_stay_monterrey,
                "Support Network Monterrey": transit.support_network_monterrey,
                "Time Knowing Support": transit.time_knowing_support,
                "Tried to Enter US": transit.tried_enter_us,
                "Support Network US": transit.support_network_us,
                "Description Support US": transit.description_support_us,
                "Been in Migration Station": transit.been_in_migration_station,
                "Suffered Aggression": transit.suffered_aggression,
                "Migration Station Location": transit.migration_station_location,
                "Description of Facts": transit.description_of_facts,
                "Filed Complaint": transit.filed_complaint,
                "Reason for No Complaint": transit.reason_no_complaint,
                "Solution Offered": transit.solution_offered,
                "Stayed in Shelter": transit.stayed_in_shelter,
                "Last Shelter": transit.last_shelter
            } for transit in result2
        ]
        # Convert list to DataFrame
        df2 = pd.DataFrame(data2)
        # Display the DataFrame using Streamlit
        st.dataframe(df2)

if __name__ == "__main__":
    dataframe_page()