import socket
import threading
import mimetypes
import os

main_page = open("index.html", "r").read()

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode("utf-8")
        print(f"Received request:\n{request}")

        get = request.split("\n")[0].split(" ")[1]
        if get == "/":
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(main_page)}\r\n"
                "\r\n"
                f"{main_page}"
            )
            client_socket.send(response.encode("utf-8"))
        else:
            try:
                ex = "." + get.split(".")[-1]
                mime_type = mimetypes.types_map[ex]
                print(f"File type: {mime_type}")

                file_path = "files" + get

                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {file_path} dont found")

                is_binary = mime_type.startswith(("image/", "video/", "audio/", "application/"))

                mode = "rb" if is_binary else "r"
                with open(file_path, mode) as file:
                    content = file.read()

                if not is_binary and isinstance(content, str):
                    content = content.encode("utf-8")

                headers = (
                    "HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {mime_type}\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    "\r\n"
                )

                client_socket.send(headers.encode("utf-8"))
                client_socket.send(content)
                
            except FileNotFoundError as e:
                error_message = "File dont found"
                response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    f"Content-Length: {len(error_message)}\r\n"
                    "\r\n"
                    f"{error_message}"
                )
                client_socket.send(response.encode("utf-8"))
                print(f"404 Error: {e}")
                
            except KeyError as e:
                error_message = f"Unsupported Media Type: {str(e)}"
                response = (
                    "HTTP/1.1 415 Unsupported Media Type\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    f"Content-Length: {len(error_message)}\r\n"
                    "\r\n"
                    f"{error_message}"
                )
                client_socket.send(response.encode("utf-8"))
                print(f"MIME type error: {e}")
                
            except Exception as e:
                error_message = f"Server error: {str(e)}"
                response = (
                    "HTTP/1.1 500 Internal Server Error\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    f"Content-Length: {len(error_message)}\r\n"
                    "\r\n"
                    f"{error_message}"
                )
                client_socket.send(response.encode("utf-8"))
                print(f"General error: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = "127.0.0.1"
port = 8080
server_socket.bind((host, port))

server_socket.listen(5)
print("Server started")

try:
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

except KeyboardInterrupt:
    print("\nStopping server...")
finally:
    server_socket.close()