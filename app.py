
import streamlit as st
from componet.interface import Component

interface = Component()

#configuração da página
st.set_page_config(
    page_title='Chat Port',
    page_icon='📃'
) 

st.header('🤖 Chat Port')
interface.sidebar()
interface.input_prompt()

