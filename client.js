// client.js
const net = require("net");
const readline = require("readline");

const HOST = "127.0.0.1";
const PORT = 5000;

const client = net.createConnection({ host: HOST, port: PORT }, () => {
  console.log("connected to server");
  askInput(); // 接続できたら対話開始
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

let nextId = 1;

// ユーザー入力を聞いて、毎回RPCを投げる
function askInput() {
  rl.question('method param1 param2...（例: reverse hello / add 10 20 / exit）> ', (line) => {
    if (line === "exit") {
      console.log("closing client...");
      rl.close();
      client.end();
      return;
    }

    const parts = line.trim().split(/\s+/);
    const method = parts[0];
    const params = parts.slice(1); // 残りは全部paramsとして送る

    const request = {
      method,
      params,
      id: nextId++,
    };

    const raw = JSON.stringify(request) + "\n";
    console.log("send raw:", raw.trim());
    client.write(raw);

    // ここで return しない → 次の入力も受け付け続ける
    askInput();
  });
}

// 受信バッファ
let buffer = "";

client.on("data", (data) => {
  buffer += data.toString();

  while (buffer.includes("\n")) {
    const idx = buffer.indexOf("\n");
    const line = buffer.slice(0, idx).trim();
    buffer = buffer.slice(idx + 1);

    if (!line) continue;

    console.log("received raw:", line);
    try {
      const resp = JSON.parse(line);
      console.log("response object:", resp);
    } catch (e) {
      console.error("JSON parse error:", e);
    }
  }
});

client.on("end", () => {
  console.log("disconnected from server");
  rl.close();
});

client.on("error", (err) => {
  console.error("client error:", err);
  rl.close();
});
