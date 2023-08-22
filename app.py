from apikey import openAIKey
from football_api import get_match_details
import os
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from premier_league_teams import  teams_mapping
from fuzzywuzzy import process

os.environ['OPENAI_API_KEY'] = openAIKey

premier_league_teams = teams_mapping.keys()


#App framework
st.title('Premier League Match Preview Tweet Generator')
prompt = st.text_input('Enter a team:')

# Prompt templates
topic_template = PromptTemplate(
    input_variables = ['topic'],
    template = '''act as a football journalist who has covered the premier league closely for 20 years. 
    I will give you the pre match odds of a game and some news about it and I want you to come up with a tweet that is exciting and gets people hyped for the game. {topic}
    Don't mention the actual odds or the form. Use the odds and form to hint at who is likelier to win. Again don't mention the odds verbatim. Note that for the form, L stands for Loss, D for draw and w for win. Most recent games are mentioned first.
    Also bear in mind the number of form games to determine how far we are into the season. Be sure to put in the shortened version of each team together as a hastag at the end. Do not put this anywhere else. For example for Arsenal v Chelsea "#ARSCHE" should be at the end.
    '''
)

# LLMs
llm = ChatOpenAI(temperature = 0.9, model= "gpt-3.5-turbo")
topic_chain = LLMChain(llm=llm, prompt=topic_template, verbose=True)

# Show stuff to screen if there is a prompt
if prompt:
    best_match, score = process.extractOne(prompt, premier_league_teams)
    if score > 80:  # You can adjust the threshold as needed
        corrected_team = best_match
        st.write(f"Generating tweet for {corrected_team} ...")
    else:
        st.write("Team not recognized. Please enter a valid Premier League team.")

    hype = get_match_details(corrected_team)
    response = topic_chain.run(hype)
    st.write(response)