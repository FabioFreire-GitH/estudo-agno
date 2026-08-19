# 1 - IMPORTS ==========================================================================================
import requests # Importa a biblioteca 'requests' para fazer requisições HTTP (como enviar dados para um servidor).
import json # Importa a biblioteca 'json' para trabalhar com dados no formato JSON (serializar e desserializar).
from pprint import pprint # Importa 'pprint' (pretty print) para imprimir estruturas de dados complexas de forma mais legível.

# Define o ID do agente com o qual queremos interagir. Este é um identificador único para o agente no servidor.
AGENT_ID = "agent_pdf"
# Constrói a URL completa para o endpoint do agente.
# 'http://localhost:7777' é o endereço do servidor onde o Agno (ou outro serviço) está rodando.
# '/agents/{AGENT_ID}/runs' é o caminho para enviar comandos/mensagens a um agente específico.
ENDPOINT = f"http://localhost:7777/agents/{AGENT_ID}/runs"

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
                                # Isso é útil para respostas longas ou em tempo real.
        },
        stream=True # Também indica ao 'requests' que a conexão deve ser mantida aberta para streaming.
    )
    # 2.1 - STREAMING (processamento)==================================================================
    # Itera sobre as linhas da resposta recebida em stream.
    # Cada 'line' aqui representa um pedaço da resposta que vem do servidor.
    for line in response.iter_lines():
        if line: # Verifica se a linha não está vazia.
            # No contexto de streaming de dados, especialmente com Server-Sent Events (SSE),
            # as linhas de dados geralmente começam com "data: ".
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
                    # Isso permite processar cada pedaço de dados à medida que ele chega.
                    yield json_data
                except json.JSONDecodeError:
                    # Se houver um erro ao tentar decodificar o JSON, ele é capturado aqui.
                    print(f"Erro ao decodificar JSON: {data}")
                    continue # Continua para a próxima linha do stream.
# 3 - PRINTA A RESPOSTA ================================================================================
'''
Evento: RunStarted
Evento: ModelRequestStarted
Evento: ModelRequestCompleted
Evento: ToolCallStarted
Evento: ToolCallCompleted
Evento: ModelRequestStarted
Evento: RunContent
Evento: RunContent
Evento: ModelRequestCompleted
Evento: RunContentCompleted
Evento: MemoryUpdateStarted
Evento: MemoryUpdateCompleted
Evento: RunCompleted
'''

def print_streaming_response(message:str):
    for event in get_response_stream(message):
        event_type = event.get("event","")
        #print(f"Evento: {event_type}") # Usa somente para capturar os eventos do agente (debug)
        # Inicio da execução do agente
        if event_type == "RunStarted":
            print("Iniciando a execução do agente...")
            print("-"*50)

        # Conteudo da resposta do agente (mensagem final)
        elif event_type == "RunContent":
            content = event.get("content", "") # Pega o conteúdo da resposta do agente (mensagem final).
            if content: # Se houver conteúdo na resposta, ele é impresso no console.
                print(f"Resposta do agente: {content}", end="", flush=True) # 'end=""' evita a quebra de linha, 'flush=True' força a impressão imediata.
                
        # Ferramenta chamada pelo agente (ex: busca no conhecimento)
        elif event_type == "ToolCallStarted":
            tool = event.get("tool", {}) # Pega informações sobre a ferramenta que o agente está chamando.
            tool_name = event.get("tool_name", "Unknown Tool")
            tool_args = event.get("tool_args", {})
            
            print(f"TOOL INICIADA: {tool_name} com argumentos: {json.dumps(tool_args, indent=2)}")

        elif event_type == "ToolCallCompleted":
            tool_name = event.get("tool_name", "Unknown Tool")
            tool_result = event.get("tool_result", {})
            print(f"TOOL FINALIZADA: {tool_name} com resultado: {json.dumps(tool_result, indent=2)}")
            print("-"*50)

        elif event_type == "RunCompleted":
            print("\nExecução do agente finalizada.")
            metrics = event.get("metrics", {})
            if metrics:
                print(f"Métricas: {json.dumps(metrics)}")
            print("-"*50)

# 4 - RUN (loop) ========================================================================================
# Este bloco de código só é executado quando o script é rodado diretamente (não quando é importado como módulo).
if __name__ == "__main__":
    message = input('Digite uma mensagem: ') # Solicita ao usuário que digite uma mensagem.
    print_streaming_response(message) # Chama a função para enviar a mensagem e imprimir a resposta em streaming.

    while True: # Inicia um loop infinito para permitir múltiplas interações com o agente.
        message = input('Digite uma mensagem: ') # Solicita ao usuário que digite uma mensagem.
        print_streaming_response(message) # Chama a função para enviar a mensagem e imprimir a resposta em streaming.
