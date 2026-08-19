from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini

from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.google import GeminiEmbedder

from fastapi import FastAPI
import uvicorn

import os
from dotenv import load_dotenv

load_dotenv()

#RAG
vector_db = ChromaDb(
    collection="pdf_agent",
    path="tmp/chromadb",
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
    db_file="tmp/agent.db"
)

agent= Agent(
    name="Agente de PDF",
    model=Gemini(id="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    instructions="""Você é um assistente focado em ajudar usuários. 
    Responda SEMPRE baseando-se na documentação fornecida. Se a resposta não estiver na base, diga educadamente que essa informação não consta no manual.""",
    db=db,
    add_history_to_context=True,
    knowledge=knowledge,
    search_knowledge=True,
    num_history_messages=3,
    debug_mode=True,
)

# FASTAPI ==========================================================================
app = FastAPI(title="Agente de PDF", description="API para responder perguntos sobre o PDF")

@app.post("/agent_pdf")
def agente_pdf(pergunta:str):
    response = agent.run(pergunta)
    message = response.messages[-1]
    return {"message":message.content}

# RUN ============================================================================== 
def main():
    uvicorn.run("exemplo1:app", host="localhost", port=8000, reload=True)

if __name__ == "__main__":
    main()