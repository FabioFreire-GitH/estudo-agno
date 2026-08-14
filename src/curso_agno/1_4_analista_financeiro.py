from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb

import os
from dotenv import load_dotenv

load_dotenv()

db = SqliteDb(db_file="tmp/data.db")

agent = Agent(
    #session_id="petrobras_session",
    #user_id="user_1",
    name="analista_financeiro",
    model=Gemini(id="gemini-3.5-flash-lite"),
    tools=[YFinanceTools()],
    instructions="Use tabelas para mostrar a informação final. Não inclua nenhum outro texto.",
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
)

#agent.print_response("Qual a cotação da Vale?",session_id="vale_session", user_id="analista_vale")
#agent.print_response("Qual a cotação da Petrobrás?", session_id="petrobras_session", user_id="analista_petrobras")
agent.print_response("Quais empresas já consultamos a cotação?", session_id="petrobras_session", user_id="analista_empresas")
