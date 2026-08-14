from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

# 1. Configuramos o "Agente" e dizemos qual IA ele vai usar
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile")
)

response = agent.run("Olá, meu nome é Fábio.")

print(response.content)

