import streamlit as st
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import os


MEMORIA = ConversationBufferWindowMemory(k=10)

def pagina_chat():

    st.header('🤖Bem-vindo ao Oráculo', divider=True)
    memoria = st.session_state.get('memoria', MEMORIA) #armazenando historicos de mensagens
    chat_ai = ChatGroq(model='llama-3.1-70b-versatile', api_key=os.getenv('TOKEN_GROQ'))
    
    
    #exibindo as mensagens
    for mensangem in memoria.buffer_as_messages:
        chat = st.chat_message(mensangem.type) #exibi quem enviou a mensagem (user ou ai)
        chat.markdown(mensangem.content) #exibidno conteúdo da mensagem

    input_usuario = st.chat_input('Fale com o oráculo') #armazena a pergunta do
    
    if input_usuario: #verificando se ha input do usuário
        memoria.chat_memory.add_user_message(input_usuario) #adicionando na memoria mensagem do usuário
        chat = st.chat_message('human')  #resposta do usuário
        chat.markdown(input_usuario) #exibidno conteúdo da mensagem do usuário
        chat = st.chat_message('ai') #resposta do chat
        with st.spinner('Buscando informação. Aguarde!'):
            resposta = chat.write_stream(chat_ai.stream(input_usuario)) #carregando a mensaagem do chatboot em tempo real
        memoria.chat_memory.add_ai_message(resposta) #adicionando na memoria mensagem do chat
        st.session_state['memoria'] = memoria #atualizando sessao com as novas mensagens
     


def main():
    pagina_chat()


if __name__ == '__main__':
    main()