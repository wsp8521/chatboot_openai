import os
import tempfile
import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

os.environ['OPENAI_API_KEY'] = os.getenv('TOKEN_OPENAI')

class ChatbootOpenai:
    def __init__(self):
        self.repository_db = 'db'
        
    def response_ai(self, model, query, vector_store):
        # Template do prompt com o contexto
        system_prompt = '''
            Responda exclusivamente com base no contexto fornecido. 
            Não faça buscas externas, nem busque informações fora do contexto, incluindo a internet ou fontes externas.
            limite-se a responder apenas no que está no contexto. 
            Se uma pergunta se referir a algo que não está presente no contexto, informe que não há informações disponíveis para responder a essa questão.
            Não faça suposições e não forneça informações não mencionadas no contexto.
            Responda de maneira detalhada, mas usando apenas os dados disponíveis no contexto.
            Exiba as resposta no formato de Markdown.
            Sempre que hover informações tabulares, exiba a tabela.
            Contexto: {context}
            '''

        # Criando histórico de mensagens
        messages = [('system', system_prompt)]
        for message in st.session_state.messages:  # Adiciona mensagens anteriores do histórico
            messages.append((message.get('role'), message.get('content')))
        
        # Adiciona a mensagem do usuário
        messages.append(('human', query))  # Usa a variável query para representar a entrada do usuário

        # Criação dos chains
        llm = ChatOpenAI(model=model, max_tokens=500)
        retriever = vector_store.as_retriever()
        prompt = ChatPromptTemplate(messages=messages)  # Cria o prompt com a lista de mensagens
        question_response_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=question_response_chain)
        
        # Obtenção da resposta
        response = chain.invoke({'input': query})
        return response.get('answer')  # Retorna a resposta da IA
    
    #Rags dos documentos
    def process_documents(self, upload_documents):
        vector_store = self.load_vector_store()
        if upload_documents:
            with st.spinner('Processando documentos...'):
                all_chunks = []
                
                # Quebra os documentos em chunks e armazena na variável
                for document in upload_documents:
                    chunks = self.__chunks_generete(file=document)
                    all_chunks.extend(chunks)
                
                # Cria ou atualiza o vector store com os chunks
                vector_store = self.__create_vector_store(chunks=all_chunks, vector_store=vector_store)
                return all_chunks


    #lendo banco de dados vectores
    def load_vector_store(self):
        if os.path.exists(self.repository_db):
            
            # Conecta ao Chroma se houver um db vector store
            vector_store = Chroma(
                persist_directory=self.repository_db,
                embedding_function=OpenAIEmbeddings()
            )
            return vector_store
        return None


    #vectore store
    def __create_vector_store(self, chunks, vector_store=None):
        if vector_store:
            vector_store.add_documents(chunks)  # Adiciona documentos ao vector store existente
        else:
            # Cria o banco de dados vector store
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=OpenAIEmbeddings(),
                persist_directory=self.repository_db
            )
        return vector_store

    def __chunks_generete(self, file):
        temp_file_path = None

        try:
            # Criação do arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name
            
            # Carrega e processa o arquivo PDF
            loader = PyPDFLoader(temp_file_path)
            docs = loader.load()
            
            # Configuração e divisão em chunks
            text_splitters = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitters.split_documents(docs)
            
            return chunks  # Retorna a lista de chunks
        
        finally:
            # Remove o arquivo temporário
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
