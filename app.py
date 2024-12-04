from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
from scripts.bar_graph import generate_bar_graph
from scripts.heat_map import generate_heat_map
from scripts.chart import generate_chart
from scripts.month_data import generate_month_list
from scripts.barangay_list import generate_barangay_list
from scripts.model import AccidentModel
import logging

app = Flask(__name__)
CORS(app)

EXCEL_FILE_PATH = 'traffic-incident.xlsx'

#Loads model upon starting the webapp
accident_model = AccidentModel()
accident_model.load_model()

@app.route('/')
def home():
    bar_graph_html = generate_bar_graph(EXCEL_FILE_PATH)
    heat_map_html = generate_heat_map(EXCEL_FILE_PATH)
    chart_2022_html = generate_chart(EXCEL_FILE_PATH, 2022)
    chart_2023_html = generate_chart(EXCEL_FILE_PATH, 2023)
    chart_2024_html = generate_chart(EXCEL_FILE_PATH, 2024)

    return render_template('index.html', bar_graph = bar_graph_html, chart_2022 = chart_2022_html, chart_2023 = chart_2023_html, chart_2024 = chart_2024_html, heat_map = heat_map_html)

@app.route('/getMonthData', methods=['POST'])
def get_month_data():
    try:
        data = request.get_json()
        logging.debug(f'Received data:{data}')
        if not data or 'year' not in data or 'month' not in data:
            raise ValueError("Invalid input data. Ensure 'year' and 'month' are provided.")
        
        year = data.get('year')
        month_name = data.get('month')
        month = datetime.strptime(month_name, "%b").month 
        logging.debug(f"Year: {year}, Month: {month_name}")


        response = generate_month_list(EXCEL_FILE_PATH, year, month)
        logging.debug(f"Response from generate_month_list: {response}")

        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error in get_month_data: {str(e)}")
        return jsonify({'error':str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict_accident():
    try:
        data = request.get_json()
        barangay = data.get('barangay')
        hour = data.get('hour')
        if barangay is None or hour is None:
            return jsonify({'error':'PLease provide barangay and hour.'}), 400
        
        try:
            hour = int(hour)
        except ValueError:
            return jsonify({'error': 'Hour must be an integer.'}), 400
    
        response = accident_model.predict_accident_chance(barangay, hour-1)
        return jsonify(response)
    except Exception as e:
        return jsonify('No results found', e), 500

@app.route('/getBarangayList', methods=['GET'])
def get_barangay_list():
    try:
        return generate_barangay_list(EXCEL_FILE_PATH)
    except Exception as e:
        return jsonify('Unable to generate list', e), 500

if __name__ == "__main__":
    app.run(debug = True)