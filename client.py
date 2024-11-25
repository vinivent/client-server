import socket
import time
from header import pack_header, calculate_checksum

def send_message(message, sock, ack_num, seq_num, corrupt=False):
    try:
        payload = message.encode('utf-8')
        checksum = calculate_checksum(payload)

        if corrupt:
            # Simula corrupção no checksum
            checksum = (checksum + 1) % 256

        header = pack_header(seq_num, ack_num, 0b00000001, checksum, len(payload))
        packet = header + payload + b'\n'
        sock.sendall(packet)
        print(f"\nPacote {'corrompido' if corrupt else 'íntegro'} enviado. (seq_num: {seq_num})")
        response = sock.recv(1024)
        return response
    except socket.timeout:
        print(f"\nTimeout: Sem resposta do servidor. (seq_num: {seq_num})\n")
        return None

def create_message(message, ack_num, seq_num):
    payload = message.encode('utf-8')
    checksum = calculate_checksum(payload)
    header = pack_header(seq_num, ack_num, 0b00000001, checksum, len(payload))
    return header + payload

def send_batch_response_per_packet(messages, sock, ack_num, seq_start, window_size):
    seq_num = seq_start
    total_messages = len(messages)
    index = 0

    while index < total_messages:
        window_end = min(index + window_size, total_messages)
        batch_packets = b''

        print(f"\nInício da Janela. Enviando mensagens {index + 1} a {window_end}.\n")

        for i in range(index, window_end):
            packet = create_message(messages[i], ack_num, seq_num)
            batch_packets += packet + b'\n'
            seq_num += 1

        # Envia lote de pacotes
        sock.sendall(batch_packets)
        print(f"Lote enviado: {index + 1} a {window_end}.")

        # Processa respostas para o lote
        for i in range(index, window_end):
            try:
                response = sock.recv(1024)
                if response == b'ACK1':
                    print(f"ACK1 recebido! Mensagem {i + 1} confirmada com sucesso.\n")
                elif response == b'ACK4':
                    print(f"ACK4 recebido! Mensagem {i + 1} corrompida. Reenviando.\n")
                    packet = create_message(messages[i], ack_num, seq_num - (window_end - i))
                    sock.sendall(packet + b'\n')
            except socket.timeout:
                print(f"Timeout ao aguardar resposta para mensagem {i + 1}.\n")

        index += window_size
        print(f"Fim da Janela.\n")

def create_client(host="localhost", port=12345, timeout=30):  # Timeout ajustado para 30 segundos
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.settimeout(timeout)  # Timeout ajustado
        try:
            seq_num = 100
            while True:
                menu_input = input("\nEscolha uma opção:\n"
                                   "1 - Enviar mensagem íntegra\n"
                                   "2 - Enviar mensagens em lote\n"
                                   "3 - Simular mensagem corrompida\n"
                                   "0 - Sair\n"
                                   "Digite sua opção: ")
                if menu_input == '0':
                    break

                if menu_input == '1':
                    message = input("\nDigite sua mensagem: ")
                    ack_num = 1
                    response = send_message(message, sock, ack_num, seq_num)
                    if response == b'ACK1':
                        print(f"\nACK1 recebido! Mensagem enviada com sucesso. (seq_num: {seq_num})\n")
                    elif response == b'ACK4':
                        print(f"\nACK4 recebido. Mensagem corrompida. (seq_num: {seq_num})\n")
                    seq_num += 1

                elif menu_input == '2':
                    num_messages = int(input("\nDigite o número de mensagens a enviar: "))
                    messages = [input(f"Digite a mensagem {i + 1}: ") for i in range(num_messages)]
                    window_size = int(input("\nDigite o tamanho da janela: "))
                    send_batch_response_per_packet(messages, sock, ack_num=1, seq_start=seq_num, window_size=window_size)
                    seq_num += num_messages

                elif menu_input == '3':
                    message = input("\nDigite sua mensagem para simular corrupção: ")
                    ack_num = 2
                    response = send_message(message, sock, ack_num, seq_num, corrupt=True)
                    if response == b'ACK4':
                        print(f"\nACK4 recebido. Mensagem corrompida detectada. (seq_num: {seq_num})\n")
                    seq_num += 1

                else:
                    print("\nOpção inválida. Tente novamente.\n")
        finally:
            print("\nEncerrando conexão.")
            sock.close()

if __name__ == "__main__":
    create_client()
