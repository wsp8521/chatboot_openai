import json
import pandas as pd
from langchain.tools import BaseTool
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from pydantic import Field, BaseModel

# prompt do system que judará o llm extrari o nome do estudante
class ExtratorDeEstudante(BaseModel):
    estudante: str = Field("Extraia o nome do estudante informado, sempre em letras minúsculas.") # #dados no formato de dicionário com extutura {'estudante':nome}

# Criando ferramenta que extrairá os dados
class ExtrairDados(BaseTool):
    name: str = "DadosDeEstudante"  # nome da ferramenta com anotação de tipo
    description: str = """Esta ferramenta extrai o histórico e preferências de um estudante de acordo com seu histórico""" ## Descrição da ferramenta que auxiliará a IA a executar a tarefa
    
    def busca_dados_de_estudante(self,estudante):
        dados = pd.read_csv("documentos/estudantes.csv") #definindo documento 
        dados_com_esse_estudante = dados[dados["USUARIO"] == estudante] #definindo a coluna que será pesquisada
        
        if dados_com_esse_estudante.empty:
            return {} #retorna vazio se o estudando informado não estiver na base de dados
        return dados_com_esse_estudante.iloc[:1].to_dict() #retorna os dados do estudante


    def _run(self, input: str, llm) -> str:
            parser = JsonOutputParser(pydantic_object=ExtratorDeEstudante)  # formatando a saído do nome do estudante
            llm = llm
            template = PromptTemplate(
                template="""Você deve analisar a {input} para extrair o nome de usuário informado. Formato de saída: {formato_saida}""",
                input_variables=["input"],  # variável de entrada
                partial_variables={"formato_saida": parser.get_format_instructions()}  # define o formatador da saída
            )
            
            chain = template | llm | parser
            response = chain.invoke({'input': input})
            dados_estudante =  response['estudante']
            dados = self.busca_dados_de_estudante(estudante=dados_estudante)
            print('Achei')
            print(dados)
            return json.dumps(dados)

