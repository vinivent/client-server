import socket
import threading
from concurrent.futures import ThreadPoolExecutor

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

receiver_window = 5
lost_packets = {3, 7}  # Pacotes que serão simulados como perdidos
protocol = "SR"  # Default: Selective Repeat


def checksum(data):
    """Calcula o checksum dos dados."""
    return sum(bytearray(data, 'utf-8')) % 256


def handle_client(conn, addr):
    """Manipula a conexão com o cliente."""
    print(f"[NEW CONNECTION] {addr} conectado.")
    global protocol, receiver_window

    try:
        while True:
            msg = conn.recv(2048).decode(FORMAT)
            if not msg:
                break

            if msg.startswith("PROTOCOL"):
                _, chosen_protocol = msg.split("|")
                protocol = chosen_protocol
                conn.send(protocol.encode(FORMAT))
                print(f"[SERVER] Protocolo negociado: {protocol}")
                continue

            parts = msg.split("|")
            if len(parts) < 3:
                print("[SERVER] Formato de pacote inválido.")
                continue

            seq_num, data, received_checksum = int(parts[0]), parts[1], int(parts[2])
            
            # Simula perda de pacotes
            if seq_num in lost_packets:
                print(f"[SERVER] Pacote {seq_num} perdido (simulado).")
                continue

            # Verifica integridade
            if checksum(data) != received_checksum:
                print(f"[SERVER] Erro de integridade no pacote {seq_num}. Enviando NAK.")
                conn.send(f"NAK|{seq_num}".encode(FORMAT))
                continue

            print(f"[SERVER] Pacote {seq_num} recebido com sucesso.")
            conn.send(f"ACK|{seq_num}".encode(FORMAT))

            if data == DISCONNECT_MESSAGE:
                break
    finally:
        conn.close()
        print(f"[SERVER] Conexão com {addr} encerrada.")


def start():
    """Inicia o servidor e aguarda conexões."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[SERVER] Servidor iniciado e aguardando conexões.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            conn, addr = server.accept()
            executor.submit(handle_client, conn, addr)


print("[SERVER] Iniciando servidor...")
start()
