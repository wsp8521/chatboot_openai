import streamlit as st

class Component:
    def __init__(self, chatboot):
        self.chatboot = chatboot
    
    def sidebar(self, model_option: list):
        self.select_model(model_option=model_option)
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
            
    
    def select_model(self, model_option: list):
        # Inicializa a chave no st.session_state, se necessário
        if 'selected_model' not in st.session_state:
            st.session_state['selected_model'] = model_option[0]  # Modelo padrão
        
        # Cria o selectbox
        selected_model = st.sidebar.selectbox(
            label='Selecione o modelo LLM',
            options=model_option,
            index=model_option.index(st.session_state['selected_model']),
            key="select_model_key"
        )

        # Atualiza o valor selecionado no session_state
        st.session_state['selected_model'] = selected_model
        return selected_model

    def input_prompt(self):
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []
        
        question = st.chat_input('Como posso ajudar?')
        if question:
            return self.__history_message(question)
        return None

    def __history_message(self, question):
        vector_store = self.chatboot.load_vector_store()
        
        if vector_store and question:
            for message in st.session_state.messages:
                st.chat_message(message.get('role')).write(message.get('content'))
            
            st.chat_message('user').write(question)
            st.session_state.messages.append({'role': 'user', 'content': question})

            with st.spinner('Buscando informação. Aguarde!'):
                response = self.chatboot.response_ai(
                    model=st.session_state["selected_model"],  # Usa o modelo selecionado
                    query=question,
                    vector_store=vector_store
                )

            st.chat_message('ai').write(response)
            st.session_state.messages.append({'role': 'ai', 'content': response})
            return response
