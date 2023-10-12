import socket
import threading
import json
import os
import base64
import uuid

HOST = '127.0.0.1'
PORT = 8082

CLIENT_MEDIA = f"CLIENT_MEDIA_{uuid.uuid4().hex}"

if not os.path.exists(CLIENT_MEDIA):
    os.mkdir(CLIENT_MEDIA)


def send_with_length(client_socket, message):
    message_length = f"{len(message):<10}"
    client_socket.sendall((message_length + message).encode('utf-8'))


def format_message(msg_type, payload):
    return json.dumps({"type": msg_type, "payload": payload})


def receive_messages():
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

            if message_data["type"] == "notification":
                print(message_data['payload']['message'])
            elif message_data["type"] == "message":
                payload = message_data['payload']
                print(f"{payload['sender']}: {payload['text']}")
            elif message_data["type"] == "connect_ack":
                print(message_data['payload']['message'])
            elif message_data["type"] == "file":
                file_name = message_data["payload"]["file_name"]
                b64_encoded_content = message_data["payload"]["content"]
                file_content = base64.b64decode(b64_encoded_content)

                client_room_folder = CLIENT_MEDIA
                if not os.path.exists(client_room_folder):
                    os.mkdir(client_room_folder)

                file_path = os.path.join(client_room_folder, file_name)

                with open(file_path, 'wb') as f:
                    f.write(file_content)

                print(f"File {file_name} downloaded successfully.")
        except json.JSONDecodeError:
            print("Received invalid JSON data.")


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((HOST, PORT))

print(f"Connected to {HOST}:{PORT}")

name = input("Enter your name: ").strip()
while not name:
    print("Name cannot be empty.")
    name = input("Enter your name: ").strip()

room = input("Enter the room: ").strip()
while not room:
    print("Room cannot be empty.")
    room = input("Enter the room you want to join: ").strip()

connect_msg = format_message("connect", {"name": name, "room": room})
send_with_length(client_socket, connect_msg)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

try:
    while True:
        text = input()
        if text.lower() == 'exit':
            break
        elif text.lower().startswith("upload:"):
            file_path = text.split(":")[1].strip()
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_content = f.read()

                file_name = os.path.basename(file_path)
                b64_encoded_content = base64.b64encode(file_content).decode('utf-8')
                upload_msg = format_message("upload", {"file_name": file_name, "content": b64_encoded_content})
                send_with_length(client_socket, upload_msg)
            else:
                print(f"File {file_path} doesn't exist.")
        elif text.lower().startswith("download:"):
            file_name = text.split(":")[1].strip()
            download_msg = format_message("download", {"file_name": file_name})
            send_with_length(client_socket, download_msg)
        else:
            message = format_message("message", {"sender": name, "room": room, "text": text})
            send_with_length(client_socket, message)
except KeyboardInterrupt:
    print("Exit")
finally:
    client_socket.close()
