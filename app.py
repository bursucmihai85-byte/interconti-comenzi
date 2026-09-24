import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import socket
from flask import Flask, render_template, request, jsonify, send_file
from order_system import (
    search_dictated_speech, 
    search_image_order,
    generate_word_document, 
    generate_whatsapp_link,
    save_learned_mapping,
    load_learned_mappings,
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

@app.route("/api/upload-image", methods=["POST"])
def api_upload_image():
    if "image" not in request.files:
        return jsonify({"found": False, "message": "Nicio imagine trimisă."}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"found": False, "message": "Fișier neselectat."}), 400
    
    image_bytes = file.read()
    mime_type = file.content_type or "image/jpeg"
    
    print(f"IMAGINE PRIMITĂ PENTRU OCR: {len(image_bytes)} bytes, tip: {mime_type}")
    results = search_image_order(image_bytes, mime_type)
    
    if not results:
        import order_system
        v_err = getattr(order_system, "LAST_VISION_ERROR", "")
        msg = f"Eroare recunoaștere: {v_err}" if v_err else "Nu am putut identifica repere în imagine sau scrisul nu a fost recunoscut."
        return jsonify({
            "found": False, 
            "message": msg,
            "vision_error": v_err
        }), 200
        
    print(f"-> [Vision] Găsite {len(results)} repere din imaginea încărcată!")
    return jsonify({
        "found": True,
        "items": results
    })

@app.route("/api/debug-vision")
def api_debug_vision():
    import order_system
    import base64
    raw_env = os.environ.get("GEMINI_API_KEY", "")
    env_info = f"len={len(raw_env)}, starts={raw_env[:5]}..." if raw_env else "NOT_SET"
    
    fallback_key = base64.b64decode("QVEuQWI4Uk42S1l3OVl1RHlQcUtJTHlPMURCbTVWNGNGUUdIV3RXUkVzVFh3ejZybkFYNlE=").decode("utf-8")
    test_key = raw_env if (raw_env and raw_env.startswith("AQ.")) else fallback_key

    # Test 1: Direct urllib with x-goog-api-key header
    raw_urllib_status = "none"
    try:
        import urllib.request, json
        u = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent'
        d = json.dumps({'contents': [{'parts': [{'text': 'ping'}]}]}).encode('utf-8')
        req = urllib.request.Request(u, data=d, headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': test_key
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            raw_urllib_status = f"SUCCESS {r.status}: {r.read().decode()[:50]}"
    except urllib.error.HTTPError as e_http:
        raw_urllib_status = f"HTTPError {e_http.code}: {e_http.read().decode()[:150]}"
    except Exception as e_raw:
        raw_urllib_status = f"ERROR: {e_raw}"
    
    client_status = "NONE"
    ping_status = "NOT_TESTED"
    if order_system.GEMINI_CLIENT:
        client_status = "INITIALIZED"
        try:
            r = order_system.GEMINI_CLIENT.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents="ping"
            )
            ping_status = f"OK: {r.text[:30]}"
        except Exception as e:
            ping_status = f"PING_ERROR: {e}"
            
    return jsonify({
        "env_GEMINI_API_KEY": env_info,
        "raw_urllib_status": raw_urllib_status,
        "client_status": client_status,
        "ping_status": ping_status,
        "last_init_error": getattr(order_system, "LAST_INIT_ERROR", ""),
        "last_vision_error": getattr(order_system, "LAST_VISION_ERROR", "")
    })

@app.route("/api/learn", methods=["POST"])
def api_learn():
    data = request.json or {}
    query = data.get("query", "").strip()
    item_data = data.get("item", {})
    if not query or not item_data:
        return jsonify({"success": False, "message": "Date incomplete."}), 400

    success = save_learned_mapping(query, item_data)
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Nu s-a putut salva asocierea."}), 500

@app.route("/api/learnings", methods=["GET"])
def api_learnings():
    mappings = load_learned_mappings()
    return jsonify({
        "success": True,
        "count": len(mappings),
        "mappings": mappings
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

