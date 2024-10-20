import socket

def iniciar_cliente(host='localhost', porta=8080):
    # Criação do socket TCP/IP
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente_socket.connect((host, porta))
        print(f"Conectado ao servidor em {host}:{porta}")

        mensagem = "Olá, servidor!"
        cliente_socket.send(mensagem.encode())

        resposta = cliente_socket.recv(1024).decode()
        print(f"Resposta do servidor: {resposta}")

    except ConnectionRefusedError:
        print("Falha ao conectar ao servidor. Certifique-se de que ele está em execução.")
    
    finally:
        cliente_socket.close()

if __name__ == "__main__":
    iniciar_cliente()
