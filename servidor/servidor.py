import socket
import hashlib

def calcular_checksum(dados):
    return hashlib.md5(dados.encode()).hexdigest()

def verificar_integridade(dados, checksum_recebido):
    checksum_calculado = calcular_checksum(dados)
    return checksum_calculado == checksum_recebido

def iniciar_servidor(host='localhost', porta=8080):
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((host, porta))
    servidor_socket.listen(5)
    print(f"Servidor escutando em {host}:{porta}")

    while True:
        conexao, endereco = servidor_socket.accept()
        print(f"Conexão estabelecida com {endereco}")

        while True:
            pacote = conexao.recv(1024).decode()
            if not pacote:
                break  

            numero_sequencia, dados, checksum_recebido = pacote.split('|')

            if verificar_integridade(dados, checksum_recebido):
                resposta = f"ACK {numero_sequencia}: recebido com sucesso."
                print(f"Pacote {numero_sequencia} recebido sem erros.")
            else:
                resposta = f"NACK {numero_sequencia}: erro na integridade dos dados."
                print(f"Erro de integridade no pacote {numero_sequencia}!")

            conexao.send(resposta.encode())

        conexao.close()
        print(f"Conexão com {endereco} encerrada")

if __name__ == "__main__":
    iniciar_servidor()
