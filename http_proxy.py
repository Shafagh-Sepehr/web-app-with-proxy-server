from scapy.all import *
from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse
from scapy.packet import NoPayload
import select
import socket
import threading


def is_http_packet(data):

    http_methods = [b"GET", b"POST", b"PUT", b"DELETE", b"HEAD", b"OPTIONS", b"PATCH"]
    http_responses = [b"HTTP/1.0", b"HTTP/1.1", b"HTTP/2.0"]

    for method in http_methods:
        if data.startswith(method):
            return True

    for response in http_responses:
        if response in data:
            return True

    return False


def is_http_request(data):
    p = HTTP(data)
    if p.haslayer(HTTPRequest):
        return True
    else:
        return False


def threaded(fn):
    def wrapper(*args, **kwargs):
        _thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        _thread.start()
        return _thread

    return wrapper


class HTTPProxy(object):

    def __init__(self, host, port, dst_host, dst_port):
        self.host = host
        self.port = port
        self.dst_host = dst_host
        self.dst_port = dst_port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(1)
        self.server.bind((self.host, self.port))

        self.stop = False

    def manipulate_http_header(self, data):
        packet = HTTPRequest(data)
        if is_http_packet(data) and is_http_request(data):
            host = packet.Host.decode()

            if host.find(":") != -1:
                host_ip, port = host.split(":")
            else:
                host_ip = host

            if host_ip == self.dst_host:
                # data = data.replace(
                #     host_ip.encode(), self.dst_host.encode()
                # )
                # server_sock.sendall(data)

                packet.Host = self.dst_host.encode()

                packet.Path = packet.Path[len("http://" + host) :]
                if len(packet.Path) == 0:
                    packet.Path = b"/"

                if packet.Referer:
                    packet.Referer = packet.Referer.replace(
                        host_ip.encode(), self.dst_host.encode()
                    )

                return bytes(packet)
            else:
                return False

    @threaded
    def tunnel(
        self, client_sock: socket.socket, server_sock: socket.socket, chunk_size=1024
    ):
        try:
            while not self.stop:

                """this line is for raising exception when connection is broken"""
                client_sock.getpeername() and server_sock.getpeername()

                r, w, x = select.select([client_sock, server_sock], [], [], 1000)

                if client_sock in r:
                    data: bytes = client_sock.recv(chunk_size)
                    if len(data) == 0:
                        break

                    new_data = self.manipulate_http_header(data)
                    if new_data:
                        server_sock.sendall(new_data)

                if server_sock in r:
                    data = server_sock.recv(chunk_size)
                    if len(data) == 0:
                        break

                    client_sock.sendall(data)

        except:
            pass
        try:
            server_sock.close()
        except:
            pass
        try:
            client_sock.close()
        except:
            pass

    def run(self) -> None:
        self.server.listen()

        while not self.stop:
            try:
                (sock, addr) = self.server.accept()
                if sock is None:
                    continue
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.dst_host, self.dst_port))
                self.tunnel(sock, client_socket)
            except KeyboardInterrupt:
                self.stop = True
            except TimeoutError as exp:
                pass
            except Exception as exp:
                print("Exception:", exp)


if __name__ == "__main__":
    tcp_bridge = HTTPProxy(
        "0.0.0.0", 8082, "10.0.2.15", 80
    )  # TODO:change destonation ip
    tcp_bridge.run()
