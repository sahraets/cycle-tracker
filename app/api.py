from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import sys
import os


load_dotenv(Path(__file__).parent.parent / '.env')


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.model import add_features, predict_fertile

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

# Default: synthetic data (safe for public repo)
DATA_PATH = os.getenv("CYCLE_DATA_PATH", "data/synthetic/cycle_data_synthetic.csv")

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "ok"})

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    date = data.get('date')
    temperature = float(data.get('temperature'))

    df = pd.read_csv(DATA_PATH)
    df = add_features(df)

    # finn nåværende syklus
    current_cycle_num = df['cycle_number'].iloc[-1]
    current_cycle = df[df['cycle_number'] == current_cycle_num].copy().reset_index(drop=True)

    # prediker
    result = predict_fertile(current_cycle)
    today = result.iloc[-1]

    return jsonify({
        "date": date,
        "temperature": temperature,
        "fertile": bool(today['fertile']),
        "coverline": float(today['coverline']),
        "cycle_day": int(today['cycle_day'])
    })

@app.route('/api/log', methods=['POST'])
def log_entry():
    data = request.get_json()
    date = data.get('date')
    temperature = data.get('temperature')
    menstruation = data.get('menstruation', False)

    df = pd.read_csv(DATA_PATH)

    if date in df['Date'].values:
        return jsonify({"error": "Entry for this date already exists"}), 400
    
    new_row = {
        'Date': date,
        'Temperature': temperature,
        'Menstruation': 'MENSTRUATION' if menstruation else None,
        'LH test': None,
        'Pregnancy test': None,
        'Had sex': None,
        'Notes': None,
        'Skipped': None,
        'Source': None,
        'Data Flag': None,
        'Menstruation Quantity': None,
        'Cervical Mucus Consistency': None,
        'Cervical Mucus Quantity': None,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    df.to_csv(DATA_PATH, index=False)

    print(f"Saving to: {DATA_PATH}")
    return jsonify({"message": "Entry saved succsessfully"})

if __name__=='__main__':
    app.run(debug=True, port=5001)