import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import json
import ast
from plotting import *
from survey import create_survey
import requests
from datetime import datetime

if __name__ == '__main__':
    np.random.seed(20)
    st.set_page_config(layout="wide", page_title="Vax Vibes")

    # Initialize session state for survey visibility
    if 'show_survey' not in st.session_state:
        st.session_state.show_survey = False

    def toggle_survey():
        st.session_state.show_survey = not st.session_state.show_survey

    # Create the fixed button using Streamlit components
    button_container = st.container()

    # Add the button with JavaScript onclick event
    button_container.markdown("""
    <style>
        .fixed-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 10px 20px;
            background-color: white;
            color: black;
            border-radius: 30px;
            border: 2px solid black;
            cursor: pointer;
            z-index: 999;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 24px;
        }
        .fixed-button:hover {
            background-color: #1991DA;
        }
    </style>
    <button class="fixed-button"
    onclick=create_survey()><b>Q</b>&nbsp;&nbsp;&nbsp;&nbsp;<i>Discover Your Vaccine Profile</i></button>
""", unsafe_allow_html=True)

    # Add Streamlit button with callback
    st.button(
        "Q Discover Your Vaccine Profile",
        key="survey_button",
        on_click=toggle_survey,
        help="Click to take the survey"
    )
    trigger_chat = False
    # Display survey when button is clicked
    if st.session_state.show_survey:
        trigger_chat = create_survey()
    
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Chat", "Patient Journey"])

    with tab1:
        # df = process_data()"Do you think the reduction in deaths and improved health shown here could be possible without vaccines?"
        # df.to_csv('sentiment_tag.csv')

        # Function to load and process data
        @st.cache_data
        def load_data():
            # Replace with your actual data loading method
            df = pd.read_csv('sentiment_tag.csv')
            df['embeddings'] = df['embeddings'].apply(ast.literal_eval)
            return df
        
        # Load data
        df = load_data()

        # Title
        st.title("Vax Vibes")

        # Cluster Network and Topic Distribution
        # Cluster Network
        st.subheader("Topic Clusters")

        bubbles = plot_bubble(df)
        st.plotly_chart(bubbles, use_container_width=True)

        st.subheader("Hot Topics")
        col1, col2 = st.columns([1,3])
        cluster = col1.selectbox("Choose your cluster", sorted(df['cluster'].unique()))
        sub = df[df['cluster']==cluster].sort_values(['neutral'])
        # Sentiment Distribution
        sentiment_data = pd.DataFrame({
            'Sentiment': ['Negative', 'Positive'],
            'Value': [
                sub['negative'].mean(),
                sub['positive'].mean()
            ]
        })
        
        fig_sentiment = px.pie(
            sentiment_data,
            values='Value',
            names='Sentiment',
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.G10
        )
        col1.plotly_chart(fig_sentiment, use_container_width=True)

        count, top = 0, 15
        # Format each post as a card
        for _, row in sub.iterrows():
            count += 1
            if count < top:
                # Create container with flexbox layout
                col2.markdown(
                    f"""
                    <div style='display: flex; 
                                justify-content: space-between; 
                                align-items: center; 
                                margin-bottom: 10px;'>
                        <div style='flex-grow: 1;'>{row['title']}</div>
                        <a href='{row['url']}' 
                        target='_blank' 
                        style='color: #FF0000; 
                                text-decoration: none; 
                                font-size: 12px; 
                                white-space: nowrap;
                                margin-left: 15px;'>
                            Read More
                        </a>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        # Create the Streamlit interface
        st.subheader("💉 My Viral Tweet")

        # User input section
        user_input = st.text_area(
            "What are you thinking right now?",
            height=100,
        )

        # Load data
        df = load_tweet_data()

        if user_input and len(user_input) > 0:
            # Get similar tweets
            similar_tweets = get_similar_tweets(user_input, df)
            for idx, row in similar_tweets.iterrows():
                display_tweet(row['tweet_text'], row['label'], idx)

        # Add some styling
        st.markdown("""
        <style>
            .stButton button {
                width: 100%;
                border-radius: 20px;
            }
            .stTextArea textarea {
                border-radius: 10px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.subheader(f"Tell Me More")
        st.write(sub[['title','url','negative','positive','neutral']], use_container_width=True)

    with tab2:
        # Initialize chat history
        if trigger_chat:
            try:
                response = requests.get('http://localhost:5002/api/get-rag-response', timeout=10)
                if response.status_code == 200:
                    message = response.json()['rag_response']
                    with st.chat_message("assistant"):
                        st.markdown(message)
            except Exception as e:
                st.write(e)

    with tab3:
        C1, C2 = st.columns([1,1])
        with C1:
            with open('patient_journey.json', 'r') as f:
                touch_points = json.load(f)
            st.write(touch_points)
        with C2:
            # Define the data points - keeping them relatively close together
            quadrant_data = [
                ('START', 0.28, 0.19),
                ('1', 0.32, 0.32),
                ('2', 0.39, 0.43),
                ('3', 0.33, 0.57),
                ('END', 0.43, 0.64)
            ]
            q_points = pd.DataFrame(quadrant_data, columns=['Name', 'Skeptic-to-Pro', 'Passive-to-Proactive'])
            
            quad_chart = create_quadrant_chart(q_points)
            st.plotly_chart(quad_chart, use_container_width=True)
            point = st.selectbox("Select Touchpoint for More Details", q_points['Name'], index=None)
            if point == '2':
                st.write("`RAG Agent Triggered` Logic/Reason")
                st.write("Agent deduced that the patient wanted to know more about realized health benefits of vaccinations.")
                cap1, cap2 = st.columns([2,1])
                cap1.image('show_patient.png',
                         caption='https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(24)00850-X/fulltext')
                cap2.write('This chart shows how vaccines have saved lives and improved health worldwide from 1974 to 2024. The orange part is the biggest, showing how the measles vaccine has saved millions of lives, added billions of years of life, and helped people stay healthy for longer.')
                st.write("`Question Triggered` Do you think the reduction in deaths and improved health shown here could be possible without vaccines?")
                st.write("`Patient Response` [SOMEWHAT LIKELY]")