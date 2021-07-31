##############################
## Title: SEOgre
## Author: Colt Sliva
## Date: 7/30/2021
##############################
import streamlit as st
import pandas as pd
import numpy as np
from random import randint
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
st.write(
    """
    # SEOgre
    ## An SEO tool for data with multiple layers
    """
)

st.image("https://i.gifer.com/3FOE.gif", width=500)

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




    fig = px.line(res, x="date", y=res.drop('Algo Updates', axis=1).columns)
    fig.add_bar(x=res["date"], y=res["Algo Updates"], name="Algo Updates")
    fig.update_xaxes(
        rangeslider_visible=True,
    )

    st.plotly_chart(fig, use_container_width=True, height=1000)
    



    # upload multiple competitors
    # upload multiple metrics
    # the key to join against is date
