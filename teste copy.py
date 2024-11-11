import os
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from pydantic import Field, BaseModel
from langchain.agents import Tool
from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor
import pandas as pd
import json

load_dotenv()

def busca_dados_de_estudante(estudante):
    dados = pd.read_csv("documentos/estudantes.csv") #definindo documento 
    dados_com_esse_estudante = dados[dados["USUARIO"] == estudante] #definindo a coluna que será pesquisada
    
    if dados_com_esse_estudante.empty:
        return {} #retorna vazio se o estudando informado não estiver na base de dados
    return dados_com_esse_estudante.iloc[:1].to_dict() #retorna os dados do estudante

# prompt do system que judará o llm extrari o nome do estudante
class ExtratorDeEstudante(BaseModel):
    
    #dados no formato de dicionário com extutura {'estudante':nome}
    estudante: str = Field("Extraia o nome do estudante informado, sempre em letras minúsculas.") 

# Criando ferramenta que extrairá os dados do estudante
class DadosEstudantes(BaseTool):
    name: str = "DadosDeEstudante"  # nome da ferramenta com anotação de tipo
    
    # Descrição da ferramenta que auxiliará a IA a executar a tarefa
    description: str = """Esta ferramenta extrai o histórico e preferências de um estudante de acordo com seu histórico"""

    # Função que irá executar a classe
    def _run(self, input: str) -> str:
        parser = JsonOutputParser(pydantic_object=ExtratorDeEstudante)  # formatando a saído do nome do estudante
        llm = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENIA'))
        template = PromptTemplate(
            template="""Você deve analisar a {input} para extrair o nome de usuário informado. Formato de saída: {formato_saida}""",
            input_variables=["input"],  # variável de entrada
            partial_variables={"formato_saida": parser.get_format_instructions()}  # define o formatador da saída
        )
        
        chain = template | llm | parser
        response = chain.invoke({'input': input})
        estudante =  response['estudante']
        dados = busca_dados_de_estudante(estudante)
        print('Achei')
        print(dados)
        return json.dumps(dados)


llm = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENIA'))
#definindo as ferramentas
dados_de_estudante = DadosEstudantes()

#registrando ferramentas em uma lista
tools = [
    Tool(name=dados_de_estudante.name,
         func=dados_de_estudante.run,
         description=dados_de_estudante.description)
]

#criando agent
prompt = hub.pull("hwchase17/openai-functions-agent")
agente = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

#executando agente
executor = AgentExecutor(agent=agente, tools=tools, verbose=True)

pergunta = "Qual os dados de Ana?"

resposta = executor.invoke({"input" : pergunta})
print(resposta['output'])
