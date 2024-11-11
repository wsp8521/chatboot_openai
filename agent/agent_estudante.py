from langchain import hub
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agent.tools import ExtrairDados


load_dotenv()

class AgentEstudante:
    def __init__(self,llm, api_key, documents):
        self.llm = ChatOpenAI(model=llm, api_key=api_key)
        self.documents = documents
     
    
    def AgentExecute(self, input):
        tools = ExtrairDados()._run(input=input, llm=self.llm)
        return tools
    
        
    
   