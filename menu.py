
import streamlit as st
from pages.input_page import input_page
from pages.dataframe_page import dataframe_page
from pages.pie_chart_page import pie_chart_page


st.set_page_config(page_title='Casa Monarca', page_icon=':butterfly:')

# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ['Input Page', 'Dataframe Visualization', 'Pie Chart'])

if page == 'Input Page':
    input_page()
elif page == 'Dataframe Visualization':
    dataframe_page()
elif page == 'Pie Chart':
    pie_chart_page()
