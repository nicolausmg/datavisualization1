import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import gspread
from google.oauth2.service_account import Credentials

# Load Google Sheet data
@st.cache_data
def load_google_sheet():
    # Load credentials from Streamlit Secrets
    creds_dict = json.loads(st.secrets["google_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])

    # Authorize and load Google Sheet
    client = gspread.authorize(creds)
    sheet = client.open("birdstrikes").sheet1
    data = sheet.get_all_records()

    # Convert to DataFrame
    return pd.DataFrame(data)

# Load data (cached)
if 'df' not in st.session_state:
    st.session_state.df = load_google_sheet()

df = st.session_state.df  

df['Flight Date'] = pd.to_datetime(df['Flight Date'], errors='coerce')
df['Year'] = df['Flight Date'].dt.year
df = df.dropna(subset=['Year'])
phase_counts = df.groupby(['Year', 'Phase of flight']).size().reset_index(name='Count')

# Create the first figure: Line Chart
fig1, axis1 = plt.subplots(figsize=(12, 6))
sns.lineplot(data=phase_counts, x='Year', y='Count', hue='Phase of flight', marker='o', ax=axis1)
axis1.set_xlabel('Year')
axis1.set_ylabel('Number of Birdstrikes')
axis1.set_title('Birdstrikes by Phase of Flight Over Time')
axis1.legend(title='Phase of Flight')
axis1.grid(True)

# Create the second figure: Stacked Bar Chart
fig2, axis2 = plt.subplots(figsize=(12, 6))
phase_pivot = phase_counts.pivot(index='Year', columns='Phase of flight', values='Count')
phase_pivot.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='tab10', alpha=0.8, ax=axis2)
axis2.set_xlabel('Year')
axis2.set_ylabel('Number of Birdstrikes')
axis2.set_title('Birdstrikes by Phase of Flight Over Time')
axis2.legend(title='Phase of Flight')
axis2.set_xticklabels(axis2.get_xticklabels(), rotation=45)
axis2.grid(axis='y', linestyle='--', alpha=0.7)

tab1, tab2 = st.tabs(["About the exercise", "Experiment: See the graphs"])


with tab1:
    """
    # Experiment: Birdstrikes

    ### Question: Excluding the Approach phase, which phase of the flight has experienced the highest number of birdstrikes between 1998 and 2002?

    #### 1. About the experiment
    The idea behind the experiment is to identify which visualization is more effective in answering the question. You will be presented with two visualizations of 
    birdstrikes, your task is to answer the question using the visualizations and you will be timed. At the end, you will be presented with the time you took to ansewr with 
    each graph and, in this way, determine the best graph to answer the proposed question.

    ##### 1.1 Data source
    As I had trouble connecting with the seaborn datasets, I used one of the datasets provided for the first group activity we had in class.

    #### 2. Why this question makes sense in a business context?

    This is a relevant business question for airlines because understanding which phase of flight (excluding approach) experiences the most birdstrikes allows them to optimize flight 
    procedures and enhance safety measures. By identifying high-risk phases like takeoff, climb or landing roll, airlines can implement preventive strategies such as adjusting flight altitudes, 
    modifying speeds or coordinating with airports for better wildlife hazard management. 

    #### 3. Challenges I Faced and Learnings
    - Connecting to Google Drive: Initially, I struggled to establish a connection between my Streamlit app and a Google Drive spreadsheet.
    I had to do a lot of research, making myself familiar with Google Cloud, creating a project, enabling the Google Sheets API and generating credentials.
    Once I had the credentials, I was able to authenticate and access the Google Sheet data.

    - Speed issus: Once connected, I noticed that the graphs took significantly longer to load compared to when the file was stored locally.
    Then I remembered form class that Streamlit re-runs the script every time an interaction occurs, my dataset was reloading on every button click, which slowed down performance.
    To solve this, I implemented Streamlit’s caching mechanism we saw in class to ensure the file loads only once per session, and that significantly improved the page loading speed.

    - Session State: We saw it in class, but it was for me still someting slightly tricky to understand. After playing around with it, I fully unserstood the concept and how to use it.

    #### 4. Is there a better chart than the other?
    Yes, I think the line chart is the best visualization to answer this question because it effectively compares trends over time while maintaining clarity, even when values are close to each other. 
    Unlike stacked bar charts, which can sometimes make it difficult to distinguish small differences between the pahses of the flight or the other years, a line chart allows us to clearly see fluctuations, 
    patterns, and rankings of birdstrikes for each flight phase across different years. 
    """

with tab2:
    """ 
    # Experiment: Birdstrikes

    ### Question: Excluding the Approach phase, which phase of the flight has experienced the highest number of birdstrikes between 1998 and 2002?
    
     #### Inctructions

    In this exercise, you will be presented with two visualizations of birdstrikes data between 1998 and 2002. Your task is to answer the question above using the visualizations.

    - Click the "Show Graph" button to display the first visualization.
    - Click the "I answered your question" button to display the second visualization.
    - Click the "Finish" button to see the time taken to answer with each visualization.
    - Click the "Reset" button to start over.

    **Note:** The Approach phase has been excluded from the visualizations to make the task more challenging since it was to obvious, in both charts, that is was the main phase with birdstrikes.

    """

    if 'selected_graph' not in st.session_state:
        st.session_state.selected_graph = np.random.choice([1, 2])  
        st.session_state.first_show = False
        st.session_state.second_show = False
        st.session_state.start_time = None  
        st.session_state.mid_time = None  
        st.session_state.end_time = None 

    if st.button("Show Graph"):
        st.session_state.first_show = True
        st.session_state.start_time = time.time()  

    if st.session_state.first_show:
        if st.session_state.selected_graph == 1:
            st.pyplot(fig1)
        else:
            st.pyplot(fig2)

        if st.button("I answered your question"):
            st.session_state.second_show = True
            st.session_state.mid_time = time.time()  

    if st.session_state.second_show:
        if st.session_state.selected_graph == 1:
            st.pyplot(fig2) 
        else:
            st.pyplot(fig1) 

        if st.button("Finish"):
            st.session_state.end_time = time.time()


    if st.session_state.start_time and st.session_state.mid_time and st.session_state.end_time:
        first_click_duration = st.session_state.mid_time - st.session_state.start_time
        second_click_duration = st.session_state.end_time - st.session_state.mid_time

        st.write(f"**Time to answer with the first graph:** {first_click_duration:.2f} seconds")
        st.write(f"**Time to answer with the second graph:** {second_click_duration:.2f} seconds")

        if second_click_duration > first_click_duration:
            st.write("**You were faster in answering using the first graph! That must be a better visualization**")
        else:
            st.write("**You were faster in answering using the second graph! That must be a better visualization**")
        if st.button("Reset"):
            st.session_state.first_show = False
            st.session_state.second_show = False
            st.session_state.start_time = None
            st.session_state.mid_time = None
            st.session_state.end_time = None
            st.session_state.selected_graph = np.random.choice([1, 2])