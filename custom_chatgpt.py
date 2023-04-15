#!/usr/bin/python3

import streamlit as st

from langchain.llms import OpenAI
from langchain import chains as chs

# Setting up the page layout
st.set_page_config(page_title='ChatGPT 🤖', layout='wide')

# Setting up the session variables
if "previous_chat" not in st.session_state.keys():
    st.session_state["previous_chat"] = list()
if "bot_chat" not in st.session_state.keys():
    st.session_state["bot_chat"] = list()
if "stored_session" not in st.session_state.keys():
    st.session_state["stored_session"] = list()
if "your_chat" not in st.session_state.keys():
    st.session_state["your_chat"] = ""

def get_text():
    text_in = st.text_input("Your prompt: ", st.session_state["your_chat"], key="input",
                            placeholder="Hello, How may I assist you?")
    return text_in   

def start_chat():
    save = dict()
    for bot_text, user_text in zip(st.session_state["bot_chat"], st.session_state["previous_chat"]):
        save["User:" + user_text] = "Bot:" + bot_text

    st.session_state["stored_session"].append(save)
    st.session_state["bot_chat"] = []
    st.session_state["previous_chat"] = []
    st.session_state["your_chat"] = ""

# Set up the Streamlit app layout
st.title("Custom ChatGPT 🤖")

# Ask the user to enter their OpenAI API key
API_KEY = st.sidebar.text_input(":blue[Enter API-KEY :]", placeholder="Paste API key (sk-...)", type="password")

if API_KEY:
    # OpenAI instance(with gpt-3.5-turbo model)
    gpt_api = OpenAI(temperature=0,
                openai_api_key=API_KEY, 
                model_name='gpt-3.5-turbo', 
                verbose=False
            )

    # Create a ConversationEntityMemory
    # The k here represents the number of entities to be stored in the memory
    if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = chs.conversation.memory.ConversationEntityMemory(llm=gpt_api, k=10)
        
    # Create a ConversationChain
    Chat = chs.ConversationChain(
            llm=gpt_api, 
            prompt=chs.conversation.prompt.ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory
        )  
else:
    st.markdown('''
        ```
        - 1. Enter API Key + Hit enter
        You can get the API key from https://platform.openai.com/account/api-keys
        ```
        ''')
    st.sidebar.warning('API key required to try this app.The API key is not stored in any form.')

st.sidebar.button("New Chat", on_click=start_chat, type='primary')

my_input = get_text()
if my_input:
    gpt_answer = Chat.run(input=my_input)  
    st.session_state["previous_chat"].append(my_input)
    st.session_state["bot_chat"].append(gpt_answer)

# User Chat
with st.expander("Conversation", expanded=True):
    for previous, bot in zip(st.session_state["previous_chat"][::-1], st.session_state["bot_chat"][::-1]):
        st.info(previous, icon="👤")
        st.success(bot, icon="🤖")

# Conversation History
if len(st.session_state['stored_session']) > 0:
    with st.sidebar.expander("History", expanded=False):
        for history in st.session_state['stored_session'][::-1]:
                st.write(history)
        