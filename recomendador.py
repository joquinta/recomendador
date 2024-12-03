# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GCvSnhWFGJTMYnl8M_VKQ3w8znTKQmb2
"""

import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.openai import OpenAIEmbedding

st.set_page_config(page_title="Pregunta lo que quieras de los modelos Hyundai", page_icon='🚙', layout="centered", initial_sidebar_state="auto", menu_items=None)

#openai.api_key = st.secrets.openai_key
try:
    openai.api_key = st.secrets["openai"]["openai_key"]
    print("API key found:", st.secrets["openai"]["openai_key"][:5] + "...")
except Exception as e:
    st.error("Error de configuración en secrets")
    st.write(e)

st.title("Pregunta lo que quieras de los modelos Hyundai 💬🚙")
st.info("No es una aplicación oficial, se basa en las fichas públicas y precios desde de cada auto", icon="📃")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hola, puedes preguntarme sobre versiones, especificaciones y precios",
        }
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    
    embedding_model = OpenAIEmbedding(
    api_key=openai.api_key,
    model="text-embedding-ada-002" 
    )
    reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
    docs = reader.load_data()
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        temperature= 1,
        system_prompt="""Eres un vendedor experto en autos marca Hyundai.
Solo puedes usar la base de conocimientos de los modelos, sus diferentes versiones por modelo y precios que te entregué. Debes revisar si hay diferentes versiones como turbo (T), manual (MT) y automáticas (AT) y mencionarlas en tus respuestas.
Debes responder las preguntas de los clientes con un lenguaje cercano y completo. Además, si hay versiones eléctricas de un modelo, menciónalas"""
    )
    index = VectorStoreIndex.from_documents(docs, similarity_top_k=10)
    return index


index = load_data()

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, streaming=True, response_length=5000
    )

if prompt := st.chat_input(
    "Comienza aquí"
):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Write message history to UI
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response_stream = st.session_state.chat_engine.stream_chat(prompt)
        st.write_stream(response_stream.response_gen)
        message = {"role": "assistant", "content": response_stream.response}
        # Add response to message history
        st.session_state.messages.append(message)
