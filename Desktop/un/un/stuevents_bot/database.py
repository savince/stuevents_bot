import csv
import os
from datetime import datetime

GUESTS_FILE = "guests.csv"

def save_guest(user_id: int, username: str, full_name: str, event_name: str):
    file_exists = os.path.isfile(GUESTS_FILE)
    
    with open(GUESTS_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Дата', 'User ID', 'Username', 'ФИО', 'Мероприятие'])
        
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            user_id,
            username,
            full_name,
            event_name
        ])