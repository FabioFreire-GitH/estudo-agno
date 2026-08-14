from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.recursive import RecursiveChunking

from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.chroma import ChromaDb

import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# 1. Banco de memória (Conversas)
# ======================
# Cria um arquivo SQLite para o agente lembrar do histórico de conversas
db = SqliteDb(db_file="tmp/data.db")

# ======================
# 2. Vector DB (RAG - Memória de Longo Prazo baseada em Documentos)
# ======================
vector_db = ChromaDb(
    collection="empresas_relatorios",
    path="tmp/Chromadb",
    # Usamos o embedder do Gemini para transformar os textos dos PDFs em números (vetores)
    embedder=GeminiEmbedder(
        #id="text-embedding-001",
        api_key=os.getenv("GOOGLE_API_KEY"),
    ),
    persistent_client=True,
)

knowledge = Knowledge(
    vector_db=vector_db,
)

# ======================
# 3. Reader (Como ler os PDFs)
# ======================
# O PDF é grande, então o "chunking" fatia o PDF em pedaços menores (chunks) de 2000 caracteres
pdf_reader = PDFReader(
    chunking_strategy=RecursiveChunking(
        chunk_size=2000,
        overlap=200,
    ),
)

# IMPORTANTE: Para isso funcionar, precisa criar uma pasta chamada "files"
# com as subpastas "PETR" e "VALE" contendo os arquivos PDF dos relatórios!
documentos_existem = False
try:
    if vector_db.collection.count() > 0:
        documentos_existem = True
except Exception:
    pass

if not documentos_existem:
    print("Base vazia. Realizando o upload e processamento dos PDFs...")
    knowledge.insert(
        path="files/PETR/",
        reader=pdf_reader,
    )
    knowledge.insert(
        path="files/VALE/",
        reader=pdf_reader,
    )
else:
    print("Base de conhecimento já carregada. Pulando inserção e economizando créditos!")

# ======================
# 4. Construção do Agente
# ======================
agent = Agent(
    name="analista_financeiro",
    model=Gemini(id="gemini-3.5-flash-lite", api_key=os.getenv("GOOGLE_API_KEY")),
    # Ferramenta para buscar cotações e dados de ações na internet
    tools=[YFinanceTools()],
    instructions="Você é uma analista e tem diferentes clientes. Lembre-se de cada cliente, suas informações e preferências.",
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    enable_user_memories=True,
    add_memories_to_context=True,
    enable_agentic_memory=True,

    # Conectando o RAG (Base de Conhecimento) ao Agente
    knowledge=knowledge,
    search_knowledge=True,  # Permite que o agente busque nos PDFs automaticamente
)

# ======================
# 5. Testes Práticos
# ======================

agent.print_response(
    "Olá, qual foi o lucro liquido da Petrobras no 2T25?"
)

agent.print_response(
    "O que foi comentado sobre o CAPEX da Vale no 2T25?"
)
