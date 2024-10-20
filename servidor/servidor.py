import socket

def iniciar_servidor(host='localhost', porta=8080):
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((host, porta))
    servidor_socket.listen(5)
    print(f"Servidor escutando em {host}:{porta}")

    while True:
        conexao, endereco = servidor_socket.accept()
        print(f"Conexão estabelecida com {endereco}")

        dados = conexao.recv(1024).decode()
        print(f"Dados recebidos: {dados}")

        conexao.send("Mensagem recebida com sucesso!".encode())

        conexao.close()
        print(f"Conexão com {endereco} encerrada")

if __name__ == "__main__":
    iniciar_servidor()
