__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from componet.interface import Component
from chat.chatboot_groq import ChatbootGroq
from chat.chatboot_openai import ChatbootOpenai

# Listas de modelos para cada provedor
model_option_groq = ['llama-3.1-70b-versatile', 'gemma2-9b-it', 'mixtral-8x7b-32768']
model_option_openai = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']

# Inicializa o componente sem um chatboot definido
interface = Component(chatboot=None)

# Configuração da página
st.set_page_config(
    page_title='Chat Porto do Itaqui',
    page_icon='📃'
)

st.header('🤖 Chat Port')

# Seção da barra lateral
with st.sidebar:
    st.header("Configuração do Modelo")

    # Escolha do provedor de modelo (Groq ou OpenAI)
    provider = st.selectbox(
        "Selecione o provedor de modelo:",
        options=["Groq", "OpenAI"],
        key="model_provider"
    )

    # Define as opções de modelo com base no provedor selecionado
    if provider == "Groq":
        model_option = model_option_groq
        interface.chatboot = ChatbootGroq()
    else:
        model_option = model_option_openai
        interface.chatboot = ChatbootOpenai()

    # Atualiza `selected_model` para um valor válido se necessário
    if 'selected_model' not in st.session_state or st.session_state['selected_model'] not in model_option:
        st.session_state['selected_model'] = model_option[0]  # Define o primeiro modelo como padrão

# Integração com o componente
interface.sidebar(model_option=model_option)
interface.input_prompt()

