import socket
import threading
import json
import os
import base64

HOST = '127.0.0.1'
PORT = 8082
SERVER_MEDIA = "SERVER_MEDIA"

if not os.path.exists(SERVER_MEDIA):
    os.mkdir(SERVER_MEDIA)

clients = []
rooms = {}

def format_message(msg_type, payload):
    return json.dumps({"type": msg_type, "payload": payload})

def send_with_length(client_socket, message):
    message_length = f"{len(message):<10}"
    client_socket.sendall((message_length + message).encode('utf-8'))

def handle_client(client_socket, client_address):
    global clients, rooms
    client_name = ""
    client_room = ""

    while True:
        try:
            length_data = client_socket.recv(10).strip()
            message_length = int(length_data)
            chunks = []
            bytes_received = 0
            while bytes_received < message_length:
                chunk = client_socket.recv(min(1024, message_length - bytes_received))
                if not chunk:
                    break
                chunks.append(chunk)
                bytes_received += len(chunk)
            message = b''.join(chunks).decode('utf-8')
            message_data = json.loads(message)

            print(f"Received: {message}")

            if message_data["type"] == "connect":
                client_name = message_data["payload"]["name"]
                client_room = message_data["payload"]["room"]
                clients_in_room = rooms.get(client_room, [])
                clients_in_room.append(client_socket)
                rooms[client_room] = clients_in_room

                ack_message = format_message("connect_ack", {"message": "Connected to the room."})
                send_with_length(client_socket, ack_message)

                notification = format_message("notification", {"message": f"{client_name} has joined the room."})
                for client in clients_in_room:
                    if client != client_socket:
                        send_with_length(client, notification)

            elif message_data["type"] == "message":
                clients_in_room = rooms.get(client_room, [])
                broadcast_message = format_message("message", {
                    "sender": client_name,
                    "room": client_room,
                    "text": message_data["payload"]["text"]
                })
                for client in clients_in_room:
                    send_with_length(client, broadcast_message)

            elif message_data["type"] == "upload":
                file_name = message_data["payload"]["file_name"]
                b64_encoded_content = message_data["payload"]["content"]
                file_content = base64.b64decode(b64_encoded_content)

                room_folder = os.path.join(SERVER_MEDIA, client_room)
                if not os.path.exists(room_folder):
                    os.mkdir(room_folder)

                file_path = os.path.join(room_folder, file_name)
                with open(file_path, 'wb') as f:
                    f.write(file_content)

                notification = format_message("notification",
                                              {"message": f"User {client_name} uploaded the {file_name} file."})
                for client in rooms[client_room]:
                    send_with_length(client, notification)

            elif message_data["type"] == "download":
                file_name = message_data["payload"]["file_name"]
                room_folder = os.path.join(SERVER_MEDIA, client_room)
                file_path = os.path.join(room_folder, file_name)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    b64_encoded_content = base64.b64encode(file_content).decode('utf-8')
                    send_data = format_message("file", {"file_name": file_name, "content": b64_encoded_content})
                    send_with_length(client_socket, send_data)
                else:
                    error_message = format_message("error", {"message": f"The {file_name} doesn't exist."})
                    send_with_length(client_socket, error_message)

        except json.JSONDecodeError:
            print(f"Error {client_address}")

    clients.remove(client_socket)
    if client_room in rooms:
        rooms[client_room].remove(client_socket)
    client_socket.close()

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server is listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            clients.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("Exit")
    finally:
        server_socket.close()