import os
import csv
from datetime import datetime

def log_chat(session_id: str, query: str, response: str, is_crisis:bool):
    
    log_file = "chat_log.csv"
    
    # Check if the log file exists and create it if it doesn't
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header only if the file is new
        if not file_exists:
            writer.writerow(["timestamp", "session_id", "query", "response","crisis_flag"])
        
        # Write the log entry
       
        writer.writerow([datetime.now().isoformat(), session_id, query, response,str(is_crisis)])