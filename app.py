__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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

