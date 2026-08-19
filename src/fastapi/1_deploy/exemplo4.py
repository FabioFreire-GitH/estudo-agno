# 1 - IMPORTS ==========================================================================================
import requests # Importa a biblioteca 'requests' para fazer requisições HTTP (como enviar dados para um servidor).
import json # Importa a biblioteca 'json' para trabalhar com dados no formato JSON (serializar e desserializar).
import streamlit as st # Importa a biblioteca 'streamlit' para criar interfaces web interativas de forma simples e rápida.

# Define o ID do agente com o qual queremos interagir. Este é um identificador único para o agente no servidor Agno.
AGENT_ID = "agent_pdf"
# Constrói a URL completa para o endpoint do agente.
# 'https://estudo-agno.onrender.com' é o endereço do servidor onde o Agno (ou outro serviço) está rodando.
# '/agents/{AGENT_ID}/runs' é o caminho para enviar comandos/mensagens a um agente específico.
ENDPOINT = f"https://estudo-agno.onrender.com/agents/{AGENT_ID}/runs"

# 2 - CONEXÃO COM O AGNO ===============================================================================

# Define uma função chamada 'get_response_stream' que recebe uma 'message' (string) como entrada.
# O objetivo desta função é enviar a mensagem para o agente e receber a resposta em "stream" (fluxo contínuo).
def get_response_stream(message:str):
    # Faz uma requisição HTTP POST para o ENDPOINT definido.
    response = requests.post(
        url=ENDPOINT, # A URL para onde a requisição será enviada.
        data={ # Os dados que serão enviados no corpo da requisição POST.
            "message": message, # A mensagem que queremos enviar ao agente.
            "stream": True,     # Indica ao servidor que queremos receber a resposta como um fluxo de dados (stream).
                                # Isso é útil para respostas longas ou em tempo real, como um chatbot.
        },
        stream=True # Também indica à biblioteca 'requests' que a conexão deve ser mantida aberta para streaming.
    )
    # 2.1 - STREAMING (processamento)==================================================================
    # Itera sobre as linhas da resposta recebida em stream.
    # Cada 'line' aqui representa um pedaço da resposta que vem do servidor.
    for line in response.iter_lines():
        if line: # Verifica se a linha não está vazia.
            # No contexto de streaming de dados, especialmente com Server-Sent Events (SSE),
            # as linhas de dados geralmente começam com o prefixo "data: ".
            if line.startswith(b"data: "):
                # Extrai a parte real dos dados removendo o prefixo "data: ".
                # 'line[len(b"data: "):]' pega a string a partir do fim do prefixo.
                data = line[len(b"data: "):]
                try:
                    # Tenta decodificar a string 'data' como um objeto JSON.
                    json_data = json.loads(data)
                    # 'yield' transforma esta função em um gerador.
                    # Ele retorna 'json_data' e pausa a execução da função,
                    # retomando de onde parou na próxima vez que for chamado.
                    # Isso permite processar cada pedaço de dados à medida que ele chega,
                    # dando uma sensação de tempo real na interface.
                    yield json_data
                except json.JSONDecodeError:
                    # Se houver um erro ao tentar decodificar o JSON, ele é capturado aqui.
                    print(f"Erro ao decodificar JSON: {data}")
                    continue # Continua para a próxima linha do stream.

# 3 - STREAMLIT ================================================================================

# Configurações iniciais da página Streamlit.
st.set_page_config(page_title="Agente CHAT PDF") # Define o título da aba do navegador.
st.title("Agente CHAT PDF") # Exibe um título principal na interface da aplicação.
# 3.1 - HISTORICO ===============================================================================
# A 'st.session_state' é uma forma de o Streamlit manter o estado de variáveis entre as reruns do script
# (por exemplo, quando o usuário digita algo ou interage com a interface).
# Se a lista de mensagens ainda não existe no estado da sessão, ela é inicializada como vazia.
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3.2 - MOSTRAR HISTORICO =======================================================================
# Itera sobre todas as mensagens armazenadas no histórico da sessão.
for msg in st.session_state.messages:
    # 'st.chat_message(msg["role"])' cria um contêiner visual para a mensagem, estilizando-a
    # como uma mensagem de "usuário" ou "assistente" (bot).
    with st.chat_message(msg["role"]):
        # Se a mensagem for do assistente e contiver dados de processamento, exibe-os em um "expander".
        # Isso permite ver detalhes técnicos sem poluir a interface principal.
        if msg["role"] == "assistant" and msg.get("process"):
            with st.expander(label="Processamento do Agente", expanded=False):
                st.json(msg["process"]) # Exibe os dados de processamento como JSON formatado.
        # Exibe o conteúdo principal da mensagem usando Markdown para formatação rica (negrito, itálico, etc.).
        st.markdown(msg["content"])

# 3.3 - INPUT DO USUARIO ========================================================================
# 'st.chat_input()' cria uma caixa de texto na parte inferior da tela, típica de interfaces de chat.
# O texto digitado pelo usuário é capturado na variável 'prompt'.
if prompt := st.chat_input("Digite sua pergunta sobre o PDF"):
    # Adiciona a pergunta do usuário ao histórico de mensagens da sessão.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Exibe a mensagem do usuário imediatamente na interface do chat.
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepara a área para a resposta do agente.
    with st.chat_message("assistant"):
        # 'st.empty()' cria um espaço reservado na interface.
        # Isso é crucial para o streaming: podemos atualizar o conteúdo deste placeholder
        # à medida que a resposta do agente vai chegando, sem recarregar a página inteira.
        response_placeholder = st.empty()
        full_response = "" # Inicializa uma string vazia para construir a resposta completa do agente.
        process_info = None # Inicializa para armazenar informações de processamento se houver.

    # 3.4 - PROCESSAMENTO E EXIBIÇÃO DA RESPOSTA EM STREAMING ======================================
    # Itera sobre os "eventos" (pedaços de dados JSON) que vêm do gerador 'get_response_stream'.
    for event in get_response_stream(prompt):
        event_type = event.get("event", "") # Pega o tipo de evento do dicionário JSON.

        # Se o evento for do tipo "ToolCallStarted", significa que o agente começou a usar uma ferramenta.
        # Ex: "buscando informações no PDF".
        if event_type == "ToolCallStarted":
            tool_name = event.get("tool", {}).get("tool_name") # Pega o nome da ferramenta.
            # 'st.status()' exibe uma mensagem de status temporária, geralmente com um spinner.
            # O 'expanded=True' faz com que os detalhes do processo sejam visíveis por padrão.
            with st.status(f"Executando {tool_name}...", expanded=True):
                # Exibe os argumentos (parâmetros) da ferramenta que está sendo chamada.
                st.json(event.get("tool", {}).get("tool_args", {}))
            process_info = event # Armazena o evento de processamento.

        # Se o evento for do tipo "RunContent", significa que o agente está enviando parte da sua resposta final.
        elif event_type == "RunContent":
            content = event.get("content", "") # Pega o pedaço do conteúdo da resposta.
            if content:
                full_response += content # Concatena o novo pedaço ao 'full_response'.
                # Atualiza o conteúdo do placeholder na interface com a resposta parcial atual.
                response_placeholder.markdown(full_response)

    # 3.5 - FINALIZAÇÃO DA RESPOSTA ================================================================
    # Após o loop de streaming terminar (quando todos os eventos foram recebidos),
    # a resposta completa é adicionada ao histórico da sessão.
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
            "process": process_info # Inclui as informações de processamento no histórico.
        }
    )
    # Garante que a resposta final completa esteja no placeholder (caso o último pedaço não tenha atualizado).
    response_placeholder.markdown(full_response)

