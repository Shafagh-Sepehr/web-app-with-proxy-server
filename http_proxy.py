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


def threaded(fn):
    def wrapper(*args, **kwargs):
        _thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        _thread.start()
        return _thread

    return wrapper


class TCPBridge(object):

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

    # @threaded
    def tunnel(self, sock: socket.socket, sock2: socket.socket, chunk_size=1024):
        try:
            while not self.stop:
                """this line is for raising exception when connection is broken"""
                sock.getpeername() and sock2.getpeername()
                r, w, x = select.select([sock, sock2], [], [], 1000)
                if sock in r:
                    data: bytes = sock.recv(chunk_size)
                    if len(data) == 0:
                        break

                    p = HTTPRequest(data)
                    # p.show()
                    if is_http_packet(data):
                        host_ip = p.Host.decode()
                        if host_ip == self.dst_host or True:
                            # data = data.replace(
                            #     host_ip.encode(), self.dst_host.encode()
                            # )
                            # sock2.sendall(data)
                            p.Host = self.dst_host.encode()
                            p.Path = p.Path.replace(
                                host_ip.encode(), self.dst_host.encode()
                            )
                            if p.Referer:
                                p.Referer = p.Referer.replace(
                                    host_ip.encode(), self.dst_host.encode()
                                )
                            sock2.sendall(bytes(p))

                if sock2 in r:
                    data = sock2.recv(chunk_size)
                    if len(data) == 0:
                        break

                    # p = HTTPRequest(data)

                    if is_http_packet(data):
                        # print(p.Host.decode())
                        # p.Host = self.dst_host
                        sock.sendall(data)
        except:
            pass
        try:
            sock2.close()
        except:
            pass
        try:
            sock.close()
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
    tcp_bridge = TCPBridge(
        "0.0.0.0", 8082, "10.0.2.15", 80
    )  # TODO:change destonation ip
    tcp_bridge.run()
