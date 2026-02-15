from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

LOGS_FILE = "call_logs.txt"

@app.route("/log_report", methods=["POST"])
def log_report():
    """Simple endpoint - just logs an issue string."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    issue = data.get("issue") or data.get("message") or data.get("args", {}).get("issue") or str(data)
    timestamp = datetime.now().isoformat()
    
    with open(LOGS_FILE, "a") as f:
        f.write(f"\n[{timestamp}] ISSUE: {issue}\n")
    
    return jsonify({"status": "logged", "issue": issue}), 200


@app.route("/webhook/call_ended", methods=["POST"])
def call_ended_webhook():
    """Webhook for Retell - only saves transcript on call_analyzed."""
    data = request.get_json()
    
    event = data.get("event", "unknown")
    call = data.get("call", {})
    
    print(f"Webhook received: {event}")

    
    with open(LOGS_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{datetime.now().isoformat()}] TRANSCRIPT\n")
        f.write(f"Call ID: {call.get('call_id')}\n")
        f.write(f"Duration: {(call.get('end_timestamp', 0) - call.get('start_timestamp', 0)) // 1000}s\n")
        f.write(f"Recording: {call.get('recording_url')}\n")
        f.write(f"\n--- CONVERSATION ---\n")
        
        transcript = call.get("transcript", "")
        if transcript:
            f.write(transcript)
        else:
            for turn in call.get("transcript_object", []):
                f.write(f"{turn.get('role', 'unknown')}: {turn.get('content', '')}\n")
        
        f.write(f"\n--- END ---\n")
    
    print(f"Transcript saved for call {call.get('call_id')}")
    return jsonify({"status": "received"}), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
