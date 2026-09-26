"""A fake obs-websocket v5 server, for testing the OBS capture backend without OBS."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import struct
import threading


class FakeOBS(threading.Thread):
    def __init__(self, password: str | None = "pw", auth: bool = True):
        super().__init__(daemon=True)
        self.password = password
        self.auth = auth
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        self.requests: list = []
        self.recording = False
        self._duration = 0
        self.ready = threading.Event()

    # -- framing -----------------------------------------------------------

    @staticmethod
    def _send(conn, payload: dict):
        body = json.dumps(payload).encode()
        n = len(body)
        if n < 126:
            head = struct.pack("!BB", 0x81, n)
        elif n < (1 << 16):
            head = struct.pack("!BBH", 0x81, 126, n)
        else:
            head = struct.pack("!BBQ", 0x81, 127, n)
        conn.sendall(head + body)

    def _recv(self, conn) -> dict | None:
        def read(n):
            buf = b""
            while len(buf) < n:
                c = conn.recv(n - len(buf))
                if not c:
                    return None
                buf += c
            return buf
        head = read(2)
        if not head:
            return None
        b1, b2 = struct.unpack("!BB", head)
        if (b1 & 0x0F) == 0x8:
            return None
        length = b2 & 0x7F
        if length == 126:
            length = struct.unpack("!H", read(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", read(8))[0]
        key = read(4) if b2 & 0x80 else None
        body = read(length) or b""
        if key:
            body = bytes(b ^ key[i % 4] for i, b in enumerate(body))
        return json.loads(body.decode())

    # -- responses ---------------------------------------------------------

    def _response(self, rtype: str, data: dict) -> dict:
        if rtype == "GetVersion":
            return {"obsVersion": "32.2.2", "obsWebSocketVersion": "5.5.4"}
        if rtype == "GetSceneCollectionList":
            return {"currentSceneCollectionName": "Untitled",
                    "sceneCollections": ["Untitled"]}
        if rtype == "GetProfileList":
            return {"currentProfileName": "Untitled", "profiles": ["Untitled"]}
        if rtype == "GetSceneList":
            return {"currentProgramSceneName": "Scene", "scenes": [{"sceneName": "Scene"}]}
        if rtype == "GetInputList":
            return {"inputs": []}
        if rtype == "GetSceneItemList":
            return {"sceneItems": []}
        if rtype == "GetRecordStatus":
            if self.recording:
                self._duration += 400
            return {"outputActive": self.recording, "outputDuration": self._duration}
        if rtype == "StartRecord":
            self.recording = True
            self._duration = 0
            return {}
        if rtype == "StopRecord":
            self.recording = False
            return {"outputPath": self.out_path}
        return {}

    # -- loop --------------------------------------------------------------

    def run(self):
        self.ready.set()
        conn, _ = self.sock.accept()
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(4096)
            if not chunk:
                return
            data += chunk
        key = ""
        for line in data.decode(errors="replace").split("\r\n"):
            if line.lower().startswith("sec-websocket-key:"):
                key = line.split(":", 1)[1].strip()
        accept = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        conn.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                      f"Connection: Upgrade\r\nSec-WebSocket-Accept: {accept}\r\n\r\n").encode())

        hello = {"op": 0, "d": {"obsWebSocketVersion": "5.5.4", "rpcVersion": 1}}
        challenge = base64.b64encode(os.urandom(16)).decode()
        salt = base64.b64encode(os.urandom(16)).decode()
        if self.auth:
            hello["d"]["authentication"] = {"challenge": challenge, "salt": salt}
        self._send(conn, hello)

        ident = self._recv(conn)
        if self.auth:
            secret = base64.b64encode(hashlib.sha256(
                (self.password + salt).encode()).digest()).decode()
            expect = base64.b64encode(hashlib.sha256(
                (secret + challenge).encode()).digest()).decode()
            if (ident.get("d") or {}).get("authentication") != expect:
                # What OBS actually does: close with 4009 rather than confirm. The client
                # must treat that as a failure, not as a successful identification.
                self.auth_ok = False
                try:
                    conn.sendall(struct.pack("!BBH", 0x88, 2, 4009))
                finally:
                    conn.close()
                return
        self.auth_ok = True
        self._send(conn, {"op": 2, "d": {"negotiatedRpcVersion": 1}})

        while True:
            msg = self._recv(conn)
            if msg is None:
                return
            if msg.get("op") != 6:
                continue
            d = msg["d"]
            self.requests.append((d["requestType"], d.get("requestData") or {}))
            self._send(conn, {"op": 7, "d": {
                "requestType": d["requestType"], "requestId": d["requestId"],
                "requestStatus": {"result": True, "code": 100},
                "responseData": self._response(d["requestType"], d.get("requestData") or {})}})
