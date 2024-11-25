import socket
import time


TAMANHO_MAXIMO_MENSAGEM = 10


def iniciar_cliente_interativo(host='127.0.0.1', porta=50500):

    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect((host, porta))

    numero_sequencia = 0  
    tamanho_janela_congestao = 1  
    janela_recebimento = (0, 0)  

    print("Bem-vindo ao Cliente de Transporte Confiável")


    while True:
        protocolo = input("Escolha o protocolo (SR para Selective Repeat / GBN para Go-Back-N): ").strip().upper()
        if protocolo in ["SR", "GBN"]:
            break
        print("Entrada inválida! Digite 'SR' para Selective Repeat ou 'GBN' para Go-Back-N.")
    
    protocolo_completo = "Selective Repeat" if protocolo == "SR" else "Go-Back-N"
    cliente_socket.send(protocolo_completo.encode())
    resposta = cliente_socket.recv(1024).decode()
    if resposta != "ACEITO":
        print("Negociação do protocolo falhou. Encerrando cliente.")
        cliente_socket.close()
        return

    print(f"Protocolo '{protocolo_completo}' negociado com sucesso!")
    print("------------------------------")

    while True:
        print("\nOpções disponíveis:")
        print("1. Enviar um único pacote")
        print("2. Enviar múltiplos pacotes (rajada)")
        print("3. Simular erro de integridade")
        print("4. Manipular número de sequência")
        print("5. Forçar NACK com erro no pacote")
        print("6. Enviar pacote para teste de timeout (sem ACK)")
        print("7. Enviar pacote que será ignorado pelo servidor")
        print("8. Enviar lote de pacotes")
        print("9. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            conteudo = input("Digite o conteúdo do pacote: ")
            numero_sequencia, tamanho_janela_congestao, janela_recebimento = enviar_pacote(
                cliente_socket, numero_sequencia, conteudo, tamanho_janela_congestao, janela_recebimento
            )

        elif opcao == '2':
            num_pacotes = int(input("Digite o número de pacotes a enviar em rajada: "))
            pacotes = [input(f"Conteúdo do pacote {i + 1}: ") for i in range(num_pacotes)]
            numero_sequencia, tamanho_janela_congestao, janela_recebimento = enviar_rajada(
                cliente_socket, pacotes, numero_sequencia, tamanho_janela_congestao, janela_recebimento
            )

        elif opcao == '3':
            checksum_errado = input("Digite um checksum incorreto para simular erro: ")
            conteudo = input("Digite o conteúdo do pacote: ")
            numero_sequencia, tamanho_janela_congestao, janela_recebimento = enviar_com_erro_checksum(
                cliente_socket, numero_sequencia, conteudo, checksum_errado, tamanho_janela_congestao, janela_recebimento
            )

        elif opcao == '4':
            seq_manipulado = int(input("Informe o número de sequência manipulado: "))
            conteudo = input("Digite o conteúdo do pacote: ")
            enviar_pacote(cliente_socket, seq_manipulado, conteudo, tamanho_janela_congestao, janela_recebimento)

        elif opcao == '5':
            conteudo = input("Digite o conteúdo do pacote para gerar NACK: ")
            numero_sequencia, tamanho_janela_congestao, janela_recebimento = enviar_forcando_nack(
                cliente_socket, numero_sequencia, conteudo, tamanho_janela_congestao, janela_recebimento
            )

        elif opcao == '6':
            conteudo = input("Digite o conteúdo do pacote: ")
            enviar_pacote_sem_ack(cliente_socket, numero_sequencia, conteudo)

        elif opcao == '7':
            conteudo = input("Digite o conteúdo do pacote a ser ignorado: ")
            enviar_pacote_para_ignorar(cliente_socket, conteudo)

        elif opcao == '8':
            num_pacotes = int(input("Digite o número de pacotes no lote: "))
            pacotes = [input(f"Conteúdo do pacote {i + 1}: ") for i in range(num_pacotes)]
            numero_sequencia, tamanho_janela_congestao, janela_recebimento = enviar_lote(
                cliente_socket, pacotes, numero_sequencia, tamanho_janela_congestao, janela_recebimento
            )

        elif opcao == '9':
            print("Encerrando o cliente...")
            break

        else:
            print("Opção inválida. Tente novamente.")

        print("------------------------------")

    cliente_socket.close()


def calcular_checksum(mensagem):
    return str(sum(ord(ch) for ch in mensagem) % 256)


def enviar_pacote(cliente_socket, seq, conteudo, janela_congestao, janela_recebimento):
    if len(conteudo) > TAMANHO_MAXIMO_MENSAGEM:
        print(f"A mensagem excede o tamanho máximo de {TAMANHO_MAXIMO_MENSAGEM} caracteres. Será truncada.")
        conteudo = conteudo[:TAMANHO_MAXIMO_MENSAGEM]
    
    checksum = calcular_checksum(conteudo)
    pacote = f"{seq}:{checksum}:{conteudo}".encode()
    print(f"Enviando pacote: {pacote.decode()}")
    cliente_socket.send(pacote)
    resposta = cliente_socket.recv(1024).decode()
    print(f"Resposta do servidor: {resposta}")
    return processar_resposta(resposta, seq, janela_congestao, janela_recebimento)


def enviar_rajada(cliente_socket, pacotes, seq, janela_congestao, janela_recebimento):
    for conteudo in pacotes:
        seq, janela_congestao, janela_recebimento = enviar_pacote(cliente_socket, seq, conteudo, janela_congestao, janela_recebimento)
    return seq, janela_congestao, janela_recebimento


def enviar_com_erro_checksum(cliente_socket, seq, conteudo, checksum_errado, janela_congestao, janela_recebimento):
    pacote = f"{seq}:{checksum_errado}:{conteudo}".encode()
    print(f"Enviando pacote com erro de integridade: {pacote.decode()}")
    cliente_socket.send(pacote)
    resposta = cliente_socket.recv(1024).decode()
    print(f"Resposta do servidor: {resposta}")
    return processar_resposta(resposta, seq, janela_congestao, janela_recebimento, atualizar_sequencia=False)


def enviar_pacote_para_ignorar(cliente_socket, conteudo):
    mensagem = f"IGNORAR:{conteudo}".encode()
    print(f"Enviando pacote para ser ignorado: {mensagem.decode()}")
    cliente_socket.send(mensagem)


def enviar_pacote_sem_ack(cliente_socket, seq, conteudo):
    mensagem = f"TIMEOUT:{seq}:{calcular_checksum(conteudo)}:{conteudo}".encode()
    print(f"Enviando pacote sem expectativa de ACK: {mensagem.decode()}")
    cliente_socket.send(mensagem)


def enviar_lote(cliente_socket, pacotes, seq, janela_congestao, janela_recebimento):
    lote = ",".join(f"{calcular_checksum(p)}:{p}" for p in pacotes)
    mensagem = f"LOTE:{seq}:{lote}".encode()
    print(f"Enviando lote de pacotes: {mensagem.decode()}")
    cliente_socket.send(mensagem)
    resposta = cliente_socket.recv(1024).decode()
    print(f"Resposta do servidor: {resposta}")
    return processar_resposta(resposta, seq + len(pacotes), janela_congestao, janela_recebimento)


def enviar_forcando_nack(cliente_socket, seq, conteudo, janela_congestao, janela_recebimento):
    checksum_errado = "000"
    pacote = f"{seq}:{checksum_errado}:{conteudo}".encode()
    print(f"Enviando pacote para forçar NACK: {pacote.decode()}")
    cliente_socket.send(pacote)
    resposta = cliente_socket.recv(1024).decode()
    print(f"Resposta do servidor: {resposta}")
    return processar_resposta(resposta, seq, janela_congestao, janela_recebimento, atualizar_sequencia=False)


def processar_resposta(resposta, seq, janela_congestao, janela_recebimento, atualizar_sequencia=True):
    try:
        conteudo, checksum_recebido = resposta.rsplit(":", 1)
        checksum_calculado = calcular_checksum(conteudo)

        if checksum_recebido != checksum_calculado:
            print("Erro no checksum da resposta.")
            return seq, janela_congestao, janela_recebimento

        ack, recebido, janela_info = conteudo.split(":")
        recebido = int(recebido)
        inicio, fim = map(int, janela_info.strip("[]").split("-"))

        janela_recebimento = (inicio, fim)
        if ack == "ACK" and atualizar_sequencia:
            seq = recebido + 1
        elif ack == "NACK":
            janela_congestao = max(1, janela_congestao // 2)

    except ValueError:
        print("Erro ao processar resposta.")
    return seq, janela_congestao, janela_recebimento

if __name__ == '__main__':
    iniciar_cliente_interativo()
