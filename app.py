import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import socket
from flask import Flask, render_template, request, jsonify, send_file
from order_system import (
    search_dictated_speech, 
    generate_word_document, 
    generate_whatsapp_link, 
    BOGDAN_PHONE
)

app = Flask(__name__, template_folder="templates", static_folder="static")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@app.route("/")
def index():
    local_ip = get_local_ip()
    return render_template("index.html", local_ip=local_ip, bogdan_phone=BOGDAN_PHONE)

@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.json or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"found": False, "message": "Textul dictat este gol."}), 400
    
    print(f"DICTAT PRIMIT: '{text}'")
    results = search_dictated_speech(text)
    
    if not results:
        return jsonify({
            "found": False, 
            "message": f"Nu am găsit niciun reper pentru: '{text}'."
        }), 200

    print(f"-> Găsite {len(results)} repere din frază!")
    return jsonify({
        "found": True,
        "items": results
    })

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.json or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"success": False, "message": "Lista de articole este goala."}), 400

    doc_path = generate_word_document(items)
    doc_name = os.path.basename(doc_path)
    
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host") or f"{get_local_ip()}:5000"
    proto = request.headers.get("X-Forwarded-Proto") or ("https" if "trycloudflare.com" in host else "http")
    base_url = f"{proto}://{host}"
    
    doc_download_url = f"{base_url}/download/{doc_name}"
    whatsapp_url = generate_whatsapp_link(items, doc_download_url)

    print(f"COMANDĂ GENERATĂ: {len(items)} repere -> {doc_name}")
    return jsonify({
        "success": True,
        "filename": doc_name,
        "download_url": f"/download/{doc_name}",
        "full_download_url": doc_download_url,
        "whatsapp_url": whatsapp_url,
        "items_count": len(items)
    })

@app.route("/download/<filename>")
def download_file(filename):
    comenzi_dir = os.path.join(os.path.dirname(__file__), "comenzi")
    file_path = os.path.join(comenzi_dir, filename)
    if os.path.exists(file_path):
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    return "Fisierul nu a fost gasit", 404

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*60)
    print(f"APLICATIA INTERCONTI ESTE PORNITA!")
    print(f"Pe telefon (Wi-Fi): http://{local_ip}:{port}")
    print(f"Pe laptop:          http://localhost:{port}")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)

