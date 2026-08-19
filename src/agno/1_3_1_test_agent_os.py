from agno.agent import Agent
from agno.db.sqlite import SqliteDb
#from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

db = SqliteDb(db_file="agno.db")

agent = Agent(
    name="Agno Assist",
    model=Gemini(id="gemini-3.5-flash-lite"),
    db=db,
)

agent_os = AgentOS(agents=[agent], db=db)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="1_3_1_test_agent_os:app", reload=True)