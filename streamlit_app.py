from pathlib import Path
import shutil

import streamlit as st
from langchain.llms import OpenAI
import pandas as pd
from dotenv import load_dotenv

from src.pandas_dataframe_agent import create_pandas_dataframe_agent_with_tools
from src.orders import get_order_items_from_csv

# Get the base directory
basepath = Path()
envars = basepath.cwd() / ".env"
load_dotenv(envars)

container = st.container()
container.title('Analytics GPT')

def ask_agent(question):
    # df = get_order_items(bot_id, storefront_name=storefront_name, start_date="2023-01-01", end_date="2023-03-07")
    df = get_order_items_from_csv("mockup_data_region.csv")

    tools = []
    llm = OpenAI(temperature=0)
    agent = create_pandas_dataframe_agent_with_tools(tools, llm, df, verbose=True, return_intermediate_steps=True)
    response = agent({"input": question})
    
    container.write(userPrompt)
    container.write(response.get("output"))
    shutil.copyfile('top_10_products_by_region.png', 'static/plot.png')
    container.markdown("[![Click me](app/static/plot.png)](https://yalo.com)")


with st.sidebar:
    st.header('Query sidebar!')

    userPrompt = st.text_area(label='What do you want to know?')
    result = st.button(label='Click for Magic')

    if result:
        ask_agent(userPrompt)
