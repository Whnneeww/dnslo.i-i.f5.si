from dnslib import DNSRecord, QTYPE
from dnslib.server import DNSResolver, DNSServer
from flask import Flask, render_template, request, redirect, url_for
import threading

app = Flask(__name__)

# DNSレコードを保持するための簡易的なデータベース（メモリ上の辞書）
dns_records = {}

class MyDNSHandler:
    def resolve(self, request, handler):
        reply = request.reply()
        q = request.q
        domain = str(q.qname).strip('.')
        if domain in dns_records:
            reply.add_answer(*dns_records[domain])
        return reply

def run_dns_server():
    handler = MyDNSHandler()
    resolver = DNSResolver(handler)
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    server.start_thread()
    print("✅ DNSサーバーがポート53で起動中...")

@app.route('/')
def index():
    return render_template('index.html', records=dns_records)

@app.route('/add', methods=['POST'])
def add_record():
    domain = request.form['domain']
    ip = request.form['ip']
    dns_records[domain] = [(ip, QTYPE.A)]
    return redirect(url_for('index'))

@app.route('/delete/<domain>')
def delete_record(domain):
    if domain in dns_records:
        del dns_records[domain]
    return redirect(url_for('index'))

if __name__ == '__main__':
    # DNSサーバーを別スレッドで実行
    dns_thread = threading.Thread(target=run_dns_server)
    dns_thread.start()
    
    # Flaskサーバーを起動
    app.run(debug=True, host='0.0.0.0', port=5000)