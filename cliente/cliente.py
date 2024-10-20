import socket
import hashlib

def calcular_checksum(dados):
    return hashlib.md5(dados.encode()).hexdigest()

def iniciar_cliente(host='localhost', porta=8080):
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente_socket.connect((host, porta))
        print(f"Conectado ao servidor em {host}:{porta}")

        mensagem = "Olá, servidor!"
        checksum = calcular_checksum(mensagem)
        pacote = f"{mensagem}|{checksum}"
        cliente_socket.send(pacote.encode())

        resposta = cliente_socket.recv(1024).decode()
        print(f"Resposta do servidor: {resposta}")

    except ConnectionRefusedError:
        print("Falha ao conectar ao servidor. Certifique-se de que ele está em execução.")
    
    finally:
        cliente_socket.close()

if __name__ == "__main__":
    iniciar_cliente()
