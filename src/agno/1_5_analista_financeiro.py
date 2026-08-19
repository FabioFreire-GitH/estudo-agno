from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb

import os
from dotenv import load_dotenv

load_dotenv()

db = SqliteDb(db_file="tmp/data.db")

agent = Agent(
    name="analista_financeiro",
    model=Gemini(id="gemini-3.5-flash-lite"),
    tools=[YFinanceTools()],
    instructions="Você é uma analista e tem diferentes clientes. Lembre-se de cada cliente, suas informações e preferências.",
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    enable_user_memories=True,
    add_memories_to_context=True,
    enable_agentic_memory=True
)

agent.print_response("Olá. prefiro as respostas em formato de tabelas, gosto de poucas informções.", session_id="petrobras_session_1", user_id="analista_petrobras")
agent.print_response("Olá. prefiro as respostas em formato de texto, gosto de bastante detalhes.", session_id="vale_session_1", user_id="analista_vale")

agent.print_response("Qual a cotação da Petrobrás?", session_id="petrobras_session_2", user_id="analista_petrobras")
agent.print_response("Qual a cotação da Vale?",session_id="vale_session_2", user_id="analista_vale")
#agent.print_response("Quais empresas já consultamos a cotação?", session_id="petrobras_session", user_id="analista_empresas")
