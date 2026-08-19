from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.firecrawl_reader import FirecrawlReader
from agno.knowledge.chunking.recursive import RecursiveChunking

from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.chroma import ChromaDb

import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# 1. Banco de memória (Conversas)
# ======================
db = SqliteDb(db_file="tmp/data.db")

# ======================
# 2. Vector DB (RAG)
# ======================
# Criamos uma coleção nova para não misturar com os relatórios da Petrobras/Vale
vector_db = ChromaDb(
    collection="docs_sistema",
    path="tmp/Chromadb_docs", 
    embedder=GeminiEmbedder(api_key=os.getenv("GOOGLE_API_KEY")),
    persistent_client=True,
)

knowledge = Knowledge(
    vector_db=vector_db,
)

# ======================
# 3. NOVO: Firecrawl Reader 
# ======================
# O FirecrawlReader se autentica com a sua chave recém-criada
firecrawl_reader = FirecrawlReader(
    api_key=os.getenv("FIRECRAWL_API_KEY"),
    mode="scrape", 
    chunking_strategy=RecursiveChunking(
        chunk_size=1500,
        overlap=200,
    ),
)

# ======================
# 4. Inserção Corrigida (String única)
# ======================

# url_alvo = "https://ajuda.moub.com.br/guia/cadastros/convenios.html"

# print("🤖 Forçando a leitura e vetorização da página de convênios...")

# # Passamos a string diretamente, e não uma lista
# knowledge.insert(
#     url=url_alvo,
#     reader=firecrawl_reader,
# )

# total_docs = vector_db._collection.count()
# print(f"📊 Sucesso! Total de documentos reais no banco: {total_docs}")

#====================

caminho_chroma = "tmp/Chromadb_docs"
banco_existe = os.path.exists(caminho_chroma) and len(os.listdir(caminho_chroma)) > 0

if not banco_existe:
    urls_essenciais = [
        'https://ajuda.moub.com.br/guia/',
        'https://ajuda.moub.com.br/guia/produtos.html',
        'https://ajuda.moub.com.br/guia/primeiros-passos.html',
        'https://ajuda.moub.com.br/guia/dashboard.html',
        'https://ajuda.moub.com.br/guia/cadastros/administradores.html',
        'https://ajuda.moub.com.br/guia/cadastros/usuarios.html',
        'https://ajuda.moub.com.br/guia/cadastros/gestores.html',
        'https://ajuda.moub.com.br/guia/cadastros/convenios.html',
        'https://ajuda.moub.com.br/guia/cadastros/beneficiarios.html',
        'https://ajuda.moub.com.br/guia/cadastros/estabelecimentos.html',
    ]



    print("🤖 Iniciando a leitura e vetorização em lote cirúrgico (Loop)...")

    # Varremos a lista de links um por um
    for url in urls_essenciais:
        print(f"📥 Processando: {url}")
        try:
            knowledge.insert(
                url=url,
                reader=firecrawl_reader,
            )
        except Exception as e:
            print(f"❌ Erro ao processar {url}: {e}")

    total_docs = vector_db._collection.count()
    print(f"\n📊 Sucesso absoluto! Total de pedaços (chunks) salvos no banco: {total_docs}")
else:
    print("🚀 Banco de dados já existe! Pulando o download e o chunking. Iniciando o Agente instantaneamente...")

# ======================
# 5. Construção do Agente
# ======================
agent = Agent(
    name="suporte_sistema",
    model=Gemini(id="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY")),
    instructions="""Você é um assistente de suporte técnico focado em ajudar usuários do sistema. 
    Responda SEMPRE baseando-se na documentação fornecida. Se a resposta não estiver na base, diga educadamente que essa informação não consta no manual.""",
    db=db,
    add_history_to_context=True,
    enable_user_memories=True,
    knowledge=knowledge,
    search_knowledge=True,
    num_history_messages=5,
    #debug_mode=True,
)

# ======================
# 6. Testes Práticos
# ======================
# Altere a pergunta de acordo com o site que você colocou lá em cima

agent.print_response("O que são Convênios no sistema MOUB e como eles funcionam?")
agent.print_response("O que são Usuários no sistema MOUB e como eles funcionam?")
agent.print_response("Em adminstradores, quais as permissões de acesso?")
agent.print_response("Sou administrador, consigo desativar ou ativar o administrador? ")
agent.print_response("não entendi? ")
#agent.print_response("Se consigo ativar ou desativar o administrador? ")


#agent.print_response("No sistema MOUB, o que é Ajuste de saldo?")
#agent.print_response("O que são Pedidos no sistema MOUB e como eles funcionam?")

