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
    print("4. Sair")
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
        print("Encerrando o cliente.")
        return False
    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")
    return True

def enviar_pacote(cliente_socket, erro=False):
    numero_sequencia = random.randint(1, 1000)
    mensagem = input("Digite a mensagem a ser enviada: ")
    checksum = calcular_checksum(mensagem)
    
    if erro:
        checksum = "erro_simulado" 

    pacote = f"{numero_sequencia}|{mensagem}|{checksum}"
    cliente_socket.send(pacote.encode())

    time.sleep(1)
    resposta = cliente_socket.recv(1024).decode()
    print(f"""
=================== Resposta do servidor ===================
 \n{resposta}\n
============================================================
""")

def atualizar_janela_de_congestionamento(cliente_socket):
    print("a fazer")

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
