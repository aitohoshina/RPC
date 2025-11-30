# server.py
import socket
import json
import threading

HOST = "127.0.0.1"
PORT = 5000


def handle_client(conn, addr):
    """1人のクライアントを担当する関数（別スレッドで動く）"""
    print("connected:", addr)
    buffer = ""

    try:
        while True:
            # クライアントから bytes を受信
            data = conn.recv(1024)
            if not data:
                # クライアントが切断したらループ終了
                break

            # bytes -> str に変換して buffer にためる
            buffer += data.decode()

            # 改行ごとに1メッセージとして処理
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                print("received raw:", line)

                # JSON文字列 -> Python dict
                try:
                    req = json.loads(line)
                except json.JSONDecodeError:
                    print("JSON parse error")
                    continue

                method = req.get("method")
                params = req.get("params", [])
                req_id = req.get("id")

                # --- ここが「対応できるメソッド」を増やす場所 ---
                result = None
                error = None

                if method == "reverse":
                    # params[0] を文字列として受け取り、反転
                    text = str(params[0]) if params else ""
                    result = text[::-1]

                elif method == "upper":
                    # 文字列を大文字にする
                    text = str(params[0]) if params else ""
                    result = text.upper()

                elif method == "len":
                    # 文字列の長さを返す
                    text = str(params[0]) if params else ""
                    result = len(text)

                elif method == "add":
                    # 数値2つを足す
                    a = params[0] if len(params) > 0 else 0
                    b = params[1] if len(params) > 1 else 0
                    try:
                        result = float(a) + float(b)
                    except ValueError:
                        error = "add expects numbers"

                else:
                    error = f"unknown method: {method}"

                # レスポンス dict を作成
                resp = {
                    "result": result,
                    "id": req_id,
                }
                if error is not None:
                    resp["error"] = error

                # dict -> JSON文字列 + 改行
                resp_raw = json.dumps(resp) + "\n"
                print("send raw:", resp_raw.strip())

                # 文字列 -> bytes で送信
                conn.sendall(resp_raw.encode())

    finally:
        print("disconnected:", addr)
        conn.close()


def main():
    # IPv4, TCP のソケット作成
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"listening on {HOST}:{PORT}")

        while True:
            # クライアントが来るまで待つ
            conn, addr = s.accept()

            # そのクライアント専用のスレッドを立てる
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            t.start()


if __name__ == "__main__":
    main()
