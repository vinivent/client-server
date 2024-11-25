import socket
import threading
from header import unpack_header, calculate_checksum, header_size

def send_ack(client_socket, ack_type, seq_num):
    try:
        client_socket.sendall(ack_type)
        print(f"{ack_type.decode()} enviado para o cliente! (seq_num: {seq_num})\n")
    except Exception as e:
        print(f"Erro ao enviar {ack_type.decode()} para o cliente: {e}")

def handle_client(client_socket):
    try:
        buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("Cliente desconectado.\n")
                break
            buffer += data

            while b'\n' in buffer:
                raw_packet, buffer = buffer.split(b'\n', 1)

                if len(raw_packet) < header_size:
                    print("Cabeçalho inválido, descartando pacote.\n")
                    continue

                header_data = raw_packet[:header_size]
                seq_num, ack_num, flags, checksum, payload_len = unpack_header(header_data)
                payload = raw_packet[header_size:header_size + payload_len]

                if len(payload) != payload_len or checksum != calculate_checksum(payload):
                    print(f"Erro no pacote: Checksum ou payload incorreto. (seq_num: {seq_num})\n")
                    send_ack(client_socket, b'ACK4', seq_num)
                    continue

                try:
                    message = payload.decode('utf-8')
                    print(f"Mensagem recebida: {message} (seq_num: {seq_num})")
                    send_ack(client_socket, b'ACK1', seq_num)
                except UnicodeDecodeError:
                    print(f"Erro ao decodificar mensagem. (seq_num: {seq_num})\n")
                    send_ack(client_socket, b'ACK4', seq_num)
    except Exception as e:
        print(f"Erro ao processar cliente: {e}")
    finally:
        client_socket.close()

def create_server(host="localhost", port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor iniciado em {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Conexão aceita de {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("\nEncerrando servidor.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    create_server()
