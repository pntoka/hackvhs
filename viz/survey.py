import streamlit as st

def create_survey():
    with st.sidebar:
        # Question 1: Slider for hesitancy scale
        st.header("Hesitancy Scale")
        hesitancy = st.slider(
            "On a scale from 0 to 10, how hesitant are you towards vaccination?",
            min_value=0,
            max_value=10,
            value=0
        )
        
        # Question 2: Circumstances for getting vaccine
        st.header("Vaccination Circumstances")
        circumstances = st.radio(
            "A new virus breaks out and it is spreading rapidly. Luckily, there exists a vaccine which is approved by the FDA. Under what circumstances would you get the vaccine?",
            options=[
                "Always",
                "If my friends recommend it to me",
                "If the government reached out and recommended it to me",
                "If the scientific community agrees the vaccine is safe",
                "Never"
            ]
        )
        
        # Question 3: Hesitancy reasons (only if hesitancy > 6)
        if hesitancy >= 6:
            st.header("Hesitancy Reasons")
            hesitancy_reason = st.text_area(
                "What makes you hesitant about vaccines?",
                height=100
            )
        
        # Question 4: Multiple choice concerns
        st.header("Primary Concerns")
        concerns = st.multiselect(
            "Which of those do you agree with most?",
            options=[
                "Hard to schedule vaccination",
                "Side effects outweighing benefits",
                "I have health conditions preventing me from getting vaccinated",
                "I am worried to be infected with the virus through the vaccination",
                "I worry about the long-term effect on my health",
                "Hard to schedule vaccination"
            ]
        )
        
        # Question 5: Opinion ratings
        st.header("Opinion Ratings")
        
        opinion1 = st.radio(
            '"I vaccinated my children because I believe in protecting them and others in my community. It\'s not just about personal choice; it\'s about social responsibility to shield those who can\'t get vaccinated, like kids with immune disorders."',
            options=["disagree", "neutral", "agree"],
            horizontal=True,
            index=None
        )
        
        opinion2 = st.radio(
            '"The body has a natural immune system for a reason. Overloading it with synthetic vaccines can disrupt its balance and lead to other health issues down the road."',
            options=["disagree", "neutral", "agree"],
            horizontal=True,
            index=None
        )
        
        opinion3 = st.radio(
            '"The rise in autoimmune diseases correlates suspiciously with the increase in vaccination schedules. I\'m not saying vaccines are the only cause, but it\'s a risk I\'m not willing to take without more definitive answers."',
            options=["disagree", "neutral", "agree"],
            horizontal=True,
            index=None
        )
        
        # Submit button
        if st.button("Submit Survey"):
            # Here you would typically save the responses to a database
            st.success("Thank you for completing the survey!")
            
            # Display summary of responses
            st.write("Your responses:")
            st.write(f"Hesitancy level: {hesitancy}/10")
            st.write(f"Vaccination circumstance: {circumstances}")
            if hesitancy >= 6:
                st.write(f"Hesitancy reason: {hesitancy_reason}")
            st.write(f"Primary concerns: {', '.join(concerns)}")
            st.write(f"Opinion ratings: {opinion1}, {opinion2}, {opinion3}")