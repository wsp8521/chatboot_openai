import streamlit as st
from chat.chatboot_openai import ChatbootOpenai

class Component:
    def __init__(self):
        self.chatboot = ChatbootOpenai()
    
    def sidebar(self):
        with st.sidebar:
            st.header("Upload de arquivo 📃")
            
            # Upload dos arquivos
            upload_file = st.file_uploader(
                label="Faça o upload de arquivos PDF",
                type=['pdf'],
                accept_multiple_files=True  # Permite inserir múltiplos arquivos
            )
            if upload_file:
                self.chatboot.process_documents(upload_file)
            
            # Chamada do método para selecionar o modelo
            self.select_model()
    
    def select_model(self):
        # Verifica se a chave 'selected_model' já existe no st.session_state
        if 'selected_model' not in st.session_state:
            
            # Define a lista de opções de modelo
            model_option = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
            
            # Cria o selectbox com uma chave única para evitar duplicações
            st.session_state.selected_model = st.sidebar.selectbox(
                label='Selecione o modelo LLM',
                options=model_option,
                key="select_model_key"  # Identificador único
            )
        return st.session_state.selected_model

    def input_prompt(self):
        # Verifica se a sessão 'messages' existe; se não, inicializa
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []  
            
        # Captura a entrada do usuário
        question = st.chat_input('Como posso ajudar?')
        
        # Só chama __history_message se houver uma pergunta válida
        if question:
            return self.__history_message(question)
        return None

    # Método de histórico de mensagens
    def __history_message(self, question):
        # Carrega o vector store
        vector_store = self.chatboot.load_vector_store()
        
        # Verifica se há um vector_store e uma pergunta
        if vector_store and question:
            # Remonta o histórico de conversas
            for message in st.session_state.messages:
                st.chat_message(message.get('role')).write(message.get('content'))
                
            # Adiciona a pergunta do usuário ao chat e ao histórico da sessão
            st.chat_message('user').write(question)
            st.session_state.messages.append({'role': 'user', 'content': question})

            with st.spinner('Buscando informação. Aguarde!'):
                # Gera a resposta da IA
                response = self.chatboot.response_ai(
                    model=st.session_state["selected_model"],  # Usa o modelo selecionado
                    query=question,
                    vector_store=vector_store
                )

            # Adiciona a resposta da IA ao chat e ao histórico da sessão
            st.chat_message('ai').write(response)
            st.session_state.messages.append({'role': 'ai', 'content': response})
            return response
