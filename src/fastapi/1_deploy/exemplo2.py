from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.os import AgentOS

from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.google import GeminiEmbedder

import os
from dotenv import load_dotenv

load_dotenv()

#RAG
vector_db = ChromaDb(
    collection="pdf_agent",
    path="tmp/fastapi/chromadb",
    embedder=GeminiEmbedder(api_key=os.getenv("GOOGLE_API_KEY")),
    persistent_client=True,
)

knowledge=Knowledge(
    vector_db=vector_db
)

knowledge.add_content(
    url="https://s3.sa-east-1.amazonaws.com/static.grendene.aatb.com.br/releases/2564_1T26.pdf",
    metadata={"source":"Grendene", "type":"pdf", "description":"Relatório Trimestral 1T26"},
    skip_if_exists=True
)

db = SqliteDb(
    session_table="agent_session",
    db_file="tmp/fastapi/agent.db"
)

agent= Agent(
    id="agent_pdf",
    name="Agente de PDF",
    model=Gemini(id="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    instructions="""
    Você é um assistente focado em ajudar usuários. 
    Responda SEMPRE baseando-se na documentação fornecida.  
    Se a resposta não estiver na base, diga educadamente que essa informação não consta no manual.
    """,
    db=db,
    knowledge=knowledge,
    search_knowledge=True,
    enable_user_memories=True,
    #add_history_to_context=True,
    #num_history_messages=3,
    debug_mode=True,
)

# AGENT OS ==========================================================================
agent_os = AgentOS(
    name="Agente de PDF",
    agents=[agent],    
)

app = agent_os.get_app()

# RUN ============================================================================== 

if __name__ == "__main__":
    agent_os.serve(app="exemplo2:app", host="0.0.0.0", port=10000, reload=True)
