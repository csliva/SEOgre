##############################
## Title: SEOgre
## Author: Colt Sliva
## Date: 7/30/2021
##############################
from re import S
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests


##############################
## Functions
##############################

def joinDF():
    df = st.session_state.dataset[0]
    for data in st.session_state.dataset[1:]:
        df = df.merge(data, on='date')
    # loop through dataframes, skipping the first
    return df
    

##############################
## State
##############################
st.set_page_config(layout="wide")

if 'dataset' not in st.session_state:
    st.session_state.dataset = []

if 'df' not in st.session_state:
    st.session_state.df = None
    

##############################
## Instructions
##############################
c1 = st.container()
col1, col2 = st.columns(2)
c2 = st.container()
c1.markdown("""
<a href='https://ipullrank.com/' style='background-color: rgb(38, 96, 242);
    width: 100%;
    display: block;
    color: white;
    text-decoration: none;
    font-weight: bold;
    padding: 2em;'> <img src='https://ipullrank.com/wp-content/uploads/2021/03/Logo-6.png' alt="iPullRank"></a>
""", unsafe_allow_html=True)
c1.write(
    """
    # SEOgre
    ## An SEO tool for data with multiple layers
    """
)
c1.write(
    """
    Drag and drop files directly from SEO data sources to overlay the information, with Google updates.
    """
)
with col1:
    st.write("""
        ### Suggested Data Sources
        * Google Search Console Exports
        * Semrush Keywords or estimated volume
        * Ahrefs Rank or estimtaed volume
    """)
with col2:
    st.write("""
        ### Suggested Data Points
        * Keywords
        * Clicks
        * Impressions
        * Backlinks
        * PageRank or Domain Rank
    """)
##############################
## Inputs
##############################
form = st.form(key='my_form')
uploaded_files = form.file_uploader("Choose files", accept_multiple_files=True)
insert = form.form_submit_button(label='Insert')


##############################
## API Calls
##############################
r = requests.get("https://ipullrank-dev.github.io/algo-worker/")
algos = pd.DataFrame(r.json())
algos['date'] = pd.to_datetime(algos["date"]).dt.strftime("%m/%d/%Y")
#st.write(algos)

##############################
## Submit event handler
##############################
if insert and uploaded_files is not None:
    gif_runner = st.image("https://cdn.dribbble.com/users/1415337/screenshots/10781083/media/0466184625e53796cfeb7d5c5918dec8.gif")
    for file in uploaded_files:
        df = pd.read_csv(file)
        # Loop through each column and prepend the short_id to each column
        for column in df:
            if "date" not in column.lower():
                min = df[column].min()
                max = df[column].max()
                df[column] = df[column].apply(lambda x: ((x-min)/(max-min))*100)
                new_col = column + " | " + file.name[:8]
                df = df.rename(columns={column: new_col})
            else:
                df = df.rename(columns={column: "date"})
                df['date'] = pd.to_datetime(df["date"]).dt.strftime("%m/%d/%Y")
        st.session_state.dataset.append(df)
    res = joinDF()

    #### Merging our Google updates into the results
    res['Algo Updates'] = 0
    for index, row in res.iterrows():
        temp = algos.loc[row['date'] == algos["date"]]
        if not temp.empty:
            res["Algo Updates"][index] = 100

    fig = px.line(res, x="date", y=res.drop('Algo Updates', axis=1).columns, height=800)
    fig.add_bar(x=res["date"], y=res["Algo Updates"], name="Algo Updates")
    fig.update_xaxes(
        rangeslider_visible=True,
    )

    gif_runner.empty()
    c2.write("## Charts")
    c2.plotly_chart(fig, use_container_width=True, height=1000)
    c2.write("## Algo Updates")
    c2.write(algos)


    # upload multiple competitors
    # upload multiple metrics
    # the key to join against is date
