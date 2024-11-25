import socket
import threading


TAMANHO_MAXIMO_MENSAGEM = 10

def iniciar_servidor(host='127.0.0.1', porta=50500):
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((host, porta))
    servidor_socket.listen()
    print(f"Servidor ativo em {host}:{porta}")
    while True:
        conexao_cliente, endereco_cliente = servidor_socket.accept()
        print(f"Cliente conectado: {endereco_cliente}")
        threading.Thread(target=processar_cliente, args=(conexao_cliente,)).start()

def calcular_checksum(dados):
    return str(sum(ord(c) for c in dados) % 256)

def processar_cliente(conexao):
    protocolo_recebido = conexao.recv(1024).decode().strip()
    if protocolo_recebido not in ["Selective Repeat", "Go-Back-N"]:
        conexao.send("ERRO".encode())
        conexao.close()
        return
    conexao.send("ACEITO".encode())
    print(f"Protocolo negociado: {protocolo_recebido}")
    print("------------------------------")

    numero_sequencia_atual = 0
    janela_recepcao = 5
    pacotes_recebidos = {}

    while True:
        mensagem = conexao.recv(1024)
        if not mensagem:
            break

        conteudo = mensagem.decode()
        print(f"Mensagem recebida: {conteudo}")

        if conteudo.startswith("IGNORAR"):
            _, dados = conteudo.split(":", 1)
            print(f"Mensagem marcada para ignorar: '{dados}'. Ignorando pacote.")
            continue

        if conteudo.startswith("LOTE"):
            _, seq_inicial, pacotes = conteudo.split(":", 2)
            seq_inicial = int(seq_inicial)
            pacotes = pacotes.split(",")
            erro_detectado = False

            for pacote in pacotes:
                checksum_recebido, dados = pacote.split(":", 1)
                if len(dados) > TAMANHO_MAXIMO_MENSAGEM:
                    print(f"Pacote excede o tamanho máximo de {TAMANHO_MAXIMO_MENSAGEM} caracteres. Truncando.")
                    dados = dados[:TAMANHO_MAXIMO_MENSAGEM]

                if calcular_checksum(dados) != checksum_recebido:
                    erro_detectado = True
                    break

            if erro_detectado:
                resposta = f"NACK:{numero_sequencia_atual}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"
            else:
                numero_sequencia_atual += len(pacotes)
                resposta = f"ACK:{seq_inicial}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"

            conexao.send(f"{resposta}:{calcular_checksum(resposta)}".encode())
            continue

        try:
            numero_sequencia, checksum_recebido, dados = conteudo.split(":")
            numero_sequencia = int(numero_sequencia)

            if len(dados) > TAMANHO_MAXIMO_MENSAGEM:
                dados_truncados = dados[:TAMANHO_MAXIMO_MENSAGEM]
                print(f"Mensagem excede o limite. Processando apenas os primeiros {TAMANHO_MAXIMO_MENSAGEM} caracteres.")
                dados = dados_truncados

            checksum_calculado = calcular_checksum(dados)
            if checksum_recebido != checksum_calculado:
                resposta = f"NACK:{numero_sequencia_atual}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"
                print(f"Erro de integridade. Enviando NACK: {resposta}")
                conexao.send(f"{resposta}:{calcular_checksum(resposta)}".encode())
                continue

            if protocolo_recebido == "Go-Back-N":
                if numero_sequencia == numero_sequencia_atual:
                    numero_sequencia_atual += 1
                    resposta = f"ACK:{numero_sequencia}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"
                else:
                    resposta = f"NACK:{numero_sequencia_atual}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"
            elif protocolo_recebido == "Selective Repeat":
                if numero_sequencia == numero_sequencia_atual:
                    numero_sequencia_atual += 1
                    while numero_sequencia_atual in pacotes_recebidos:
                        numero_sequencia_atual += 1
                    resposta = f"ACK:{numero_sequencia}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"
                else:
                    pacotes_recebidos[numero_sequencia] = dados
                    resposta = f"ACK:{numero_sequencia}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"

            conexao.send(f"{resposta}:{calcular_checksum(resposta)}".encode())
            print(f"Resposta enviada: {resposta}")

        except ValueError:
            resposta = f"NACK:{numero_sequencia_atual}:[{numero_sequencia_atual}-{numero_sequencia_atual + janela_recepcao - 1}]"
            print(f"Erro no formato da mensagem. Enviando NACK: {resposta}")
            conexao.send(f"{resposta}:{calcular_checksum(resposta)}".encode())

    conexao.close()
    print("Conexão com o cliente encerrada.")

if __name__ == '__main__':
    iniciar_servidor()
