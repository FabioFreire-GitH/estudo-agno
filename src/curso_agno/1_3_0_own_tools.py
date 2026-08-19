from agno.agent import Agent
from agno.tools.tavily import TavilyTools
#from agno.models.groq import Groq
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

def celsius_to_fh(temp_celsius: float):
    """
    Converte uma temperatura de Celsius para Fahrenheit.
  
    Args:
        temp_celsius (float): A temperatura em graus Celsius.

    Returns:
        float: A temperatura convertida para graus Fahrenheit.
    """
    return (temp_celsius * 9/5)+ 32

agent = Agent(
    #model=Groq(id="llama-3.3-70b-versatile"),
    model=Gemini(id="gemini-3.5-flash-lite"),
    tools=[
        TavilyTools(),
        celsius_to_fh,
        ],
    debug_mode=True
)

agent.print_response("Use suas ferramentes para pesquisar a temperatura de hoje no Rio de janeiro em Fahrenheit")

