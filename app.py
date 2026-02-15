from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

LOGS_FILE = "call_logs.txt"

def save_log(log_entry):
    with open(LOGS_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{log_entry['timestamp']}] {log_entry['type'].upper()}\n")
        if log_entry.get('severity'):
            f.write(f"Severity: {log_entry['severity']}\n")
        if log_entry.get('call_id'):
            f.write(f"Call ID: {log_entry['call_id']}\n")
        f.write(f"Message: {log_entry['message']}\n")
        if log_entry.get('metadata'):
            f.write(f"Metadata: {json.dumps(log_entry['metadata'], indent=2)}\n")

@app.route("/log_report", methods=["POST"])
def log_report():
    """
    Single endpoint for Retell bot to log reports, bugs, queries, etc.
    
    Expected payload:
    {
        "type": "bug" | "report" | "query" | "observation",
        "message": "description of the issue",
        "severity": "low" | "medium" | "high" (optional),
        "call_id": "retell call id" (optional),
        "metadata": {} (optional extra data)
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": data.get("type", "report"),
        "message": data.get("message", ""),
        "severity": data.get("severity", "medium"),
        "call_id": data.get("call_id"),
        "metadata": data.get("metadata", {})
    }
    
    save_log(log_entry)
    
    print(f"[{log_entry['timestamp']}] {log_entry['type'].upper()}: {log_entry['message']}")
    
    return jsonify({"status": "logged", "entry": log_entry}), 200


@app.route("/webhook/call_ended", methods=["POST"])
def call_ended_webhook():
    """
    Webhook endpoint for Retell to send call data after call ends.
    This captures the full transcript automatically.
    
    Set this URL in your Retell dashboard under Webhooks.
    """
    data = request.get_json()
    
    # Retell sends call_id, transcript, recording_url, etc.
    call_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "transcript",
        "call_id": data.get("call_id"),
        "transcript": data.get("transcript", []),
        "recording_url": data.get("recording_url"),
        "call_duration": data.get("call_duration"),
        "metadata": data
    }
    
    # Save transcript to txt file
    with open(LOGS_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{call_data['timestamp']}] TRANSCRIPT\n")
        f.write(f"Call ID: {call_data['call_id']}\n")
        f.write(f"Duration: {call_data['call_duration']}\n")
        f.write(f"Recording: {call_data['recording_url']}\n")
        f.write(f"Transcript:\n")
        for turn in call_data.get('transcript', []):
            role = turn.get('role', 'unknown')
            content = turn.get('content', '')
            f.write(f"  {role}: {content}\n")
    
    print(f"Call ended - transcript saved to {LOGS_FILE}")
    
    return jsonify({"status": "received"}), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
