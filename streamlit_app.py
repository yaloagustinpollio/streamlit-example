from pathlib import Path
import streamlit as st
from langchain.llms import OpenAI
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
from src.pandas_dataframe_agent import create_pandas_dataframe_agent_with_tools
from src.orders import get_order_items_from_csv
import os


# Get the base directory
basepath = Path()
envars = basepath.cwd() / ".env"
load_dotenv(envars)

container = st.container()
container.title('Analytics GPT')

def ask_agent(question):
    # df = get_order_items(bot_id, storefront_name=storefront_name, start_date="2023-01-01", end_date="2023-03-07")
    try:
        os.remove("plot.png")
    except:
        pass
    
    df = get_order_items_from_csv("mockup_data_region.csv")

    tools = []
    llm = OpenAI(temperature=0)
    agent = create_pandas_dataframe_agent_with_tools(tools, llm, df, verbose=True, return_intermediate_steps=True)
    
    list_plot = ['graph', 'chart', 'plot']
    if any(word in question.lower() for word in list_plot):
        question = question + ". Save as plot.png and don't cut the labels of the plot."
    else:
        question = question
    response = agent({"input": question})
    return response


with st.sidebar:
    st.header('Query sidebar!')

    userPrompt = st.text_area(label='What do you want to know?')
    result = st.button(label='Click for Magic')

    if result:
        response= ask_agent(userPrompt)

        with container:
            #container.write(userPrompt)
            try:
                image = Image.open('plot.png')
                st.image(image, caption='plot')
                #os.remove("plot.png")
            except:
                st.header(response.get("output"))
