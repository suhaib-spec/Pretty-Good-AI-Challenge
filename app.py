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
    """Webhook for Retell call events - saves full transcript."""
    data = request.get_json()
    
    # Log raw payload for debugging
    print(f"Webhook received: {json.dumps(data, indent=2)}")
    
    event = data.get("event", "unknown")
    call = data.get("call", {})
    
    with open(LOGS_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"[{datetime.now().isoformat()}] {event.upper()}\n")
        f.write(f"Call ID: {call.get('call_id')}\n")
        
        if event == "call_analyzed":
            f.write(f"Duration: {call.get('end_timestamp', 0) - call.get('start_timestamp', 0)}ms\n")
            f.write(f"Recording: {call.get('recording_url')}\n")
            f.write(f"\n--- TRANSCRIPT ---\n")
            
            transcript = call.get("transcript", "")
            if transcript:
                f.write(transcript)
            else:
                # Try transcript_object for structured format
                transcript_obj = call.get("transcript_object", [])
                for turn in transcript_obj:
                    role = turn.get("role", "unknown")
                    content = turn.get("content", "")
                    f.write(f"{role}: {content}\n")
            
            f.write(f"\n--- END TRANSCRIPT ---\n")
        
        elif event == "call_ended":
            f.write(f"Disconnection reason: {call.get('disconnection_reason')}\n")
    
    print(f"Webhook processed: {event}")
    return jsonify({"status": "received"}), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
