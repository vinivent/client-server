import socket
import hashlib
import random
import time

def calcular_checksum(dados):
    return hashlib.md5(dados.encode()).hexdigest()

def exibir_menu():
    print("\nMenu de Opções:")
    print("1. Enviar pacote normal")
    print("2. Simular erro de integridade")
    print("3. Atualizar a janela de congestionamento")
    print("4. Escolher estratégia para lidar com erros.")
    print("5. Sair")
    opcao = input("Escolha uma opção: ")
    return opcao

def processar_opcao(opcao, cliente_socket):
    if opcao == '1':
        enviar_pacote(cliente_socket, erro=False)
    elif opcao == '2':
        enviar_pacote(cliente_socket, erro=True)
    elif opcao == '3':
        atualizar_janela_de_congestionamento(cliente_socket)
    elif opcao == '4':
        negociar_protocolo(cliente_socket)
    elif opcao == '5':
        print("Encerrando o cliente.")
        return False
    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")
    return True

def enviar_pacote(cliente_socket, erro=False):
    numero_sequencia = random.randint(1, 1000)
    mensagem = input("Digite a mensagem a ser enviada: ")
    checksum = calcular_checksum(mensagem)
    
    # Cria o pacote original
    pacote_original = f"{numero_sequencia}|{mensagem}|{checksum}"
    
    if erro:
        tipo_erro = random.choice(["faltando", "incorreto"])
        
        if tipo_erro == "faltando":
            pacote_enviado = f"{numero_sequencia}|{mensagem}|"  
        else: 
            print(f"\nHash da mensagem enviada: {checksum}")
            pacote_enviado = f"{numero_sequencia}|{mensagem}|{checksum[::-1]}"  
    else:
        pacote_enviado = pacote_original

    cliente_socket.send(pacote_enviado.encode())

    time.sleep(1)
    resposta = cliente_socket.recv(1024).decode()

    print(f"\nPacote enviado: {pacote_enviado}")
    print(f"Pacote recebido pelo servidor: {pacote_enviado}\n")

    if "CONFIRMACAO_NEGATIVA" in resposta:
        print(f"\nConfirmação negativa recebida para o pacote: {pacote_enviado}. Reenviando o pacote.")
        cliente_socket.send(pacote_original.encode())  # Reenvia o pacote original
        print(f"Pacote reenviado: {pacote_original}")
    else:
        print(f"""
=================== Resposta do servidor ===================
 \n{resposta}\n
============================================================
""")

def atualizar_janela_de_congestionamento(cliente_socket):
    nova_janela = random.randint(1, 10) 
    mensagem = f"ATUALIZAR_JANELA|{nova_janela}"
    cliente_socket.send(mensagem.encode())
    print(f"Mensagem enviada para atualizar a janela: {mensagem}")

    time.sleep(1)
    resposta = cliente_socket.recv(1024).decode()
    print(f"\nJanela de congestionamento atualizada: {resposta}")

def negociar_protocolo(cliente_socket):
    print("Escolha o protocolo:")
    print("1. Go-Back-N")
    print("2. Repetição Seletiva")
    
    opcao = input("Digite o número da sua escolha: ").strip()
    
    if opcao == '1':
        protocolo = "Go-Back-N"
    elif opcao == '2':
        protocolo = "Repetição Seletiva"
    else:
        print("Opção inválida. Usando Go-Back-N como padrão.")
        protocolo = "Go-Back-N" 

    mensagem = f"PROTOCOLO|{protocolo}"
    cliente_socket.send(mensagem.encode())
    print(f"Mensagem enviada para negociação de protocolo: {mensagem}")

    time.sleep(1)
    resposta = cliente_socket.recv(1024).decode()
    print(f"\nProtocolo negociado com o servidor: {resposta}")

def iniciar_cliente(host='localhost', porta=8080):
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente_socket.connect((host, porta))
        print(f"Conectado ao servidor em {host}:{porta}")

        continuar = True
        while continuar:
            opcao = exibir_menu()
            continuar = processar_opcao(opcao, cliente_socket)

    except ConnectionRefusedError:
        print("Falha ao conectar ao servidor. Certifique-se de que ele está em execução.")
    finally:
        cliente_socket.close()

if __name__ == "__main__":
    iniciar_cliente()
