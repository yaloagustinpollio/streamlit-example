# %%
# from langchain.agents import create_pandas_dataframe_agent
from src.langchain_scripts.demo.pandas_dataframe_agent import create_pandas_dataframe_agent_with_tools
from src.langchain_scripts.demo.prettify import Prettify
from langchain.llms import OpenAI
import pandas as pd
from src.data.orders import get_order_items
from pathlib import Path
from dotenv import load_dotenv

# Get the base directory
basepath = Path()
basedir = str(basepath.cwd())
envars = basepath.cwd() / ".env"
load_dotenv(envars)

# ---------------------------------------------------------------------------- #
#                                GET ORDER DATA                                #
# ---------------------------------------------------------------------------- #
bot_id = "mondelez-mx-b2b"
storefront_name = "mondelez-mx-b2b-ng"
df = get_order_items(bot_id, storefront_name=storefront_name, start_date="2023-01-01", end_date="2023-03-07")
# df = get_order_items("sample_data.csv")

tools = []
llm = OpenAI(temperature=0)
# ---------------------------------------------------------------------------- #
#                      CREATE PANDAS AGENT ON TOP OF DATA                      #
# ---------------------------------------------------------------------------- #
agent = create_pandas_dataframe_agent_with_tools(tools, llm, df, verbose=True, return_intermediate_steps=True)


# %%
# ---------------------------------------------------------------------------- #
#                                  QUERY AGENT                                 #
# ---------------------------------------------------------------------------- #
question = "create a table where the create date of the order was after 16h and where the total amount was higher than 100"
response = agent({"input": question})
print(question)
# response["intermediate_steps"][0][1]
# response["intermediate_steps"][-1][1].values

# %%
