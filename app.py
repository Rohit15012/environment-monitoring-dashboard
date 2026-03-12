from flask import Flask, render_template, jsonify, Response, request
import random, datetime, csv, io, requests

app = Flask(__name__)
sensor_history = []

WEATHER_API_KEY = "8c3996b49bbb4e5d95763110260202"
WEATHER_URL = "http://api.weatherapi.com/v1/current.json"

def generate_sensor_data():
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "PM2_5": round(random.uniform(30, 150), 2),
        "CO2": round(random.uniform(350, 600), 2),
        "pH": round(random.uniform(6.0, 8.5), 2),
        "Turbidity": round(random.uniform(2, 8), 2),
        "Lead_Level": round(random.uniform(0.01, 0.09), 3)
    }

THRESHOLDS = {
    "PM2_5": 60,
    "CO2": 450,
    "Lead_Level": 0.05
}

@app.route("/")
def dashboard():
    city = request.args.get("city", "Pune")
    url = f"http://api.weatherapi.com/v1/current.json?key=8c3996b49bbb4e5d95763110260202&q={city}"
    data = requests.get(url).json()

    weather = data["current"]

    return render_template(
        "index.html",
        city=city,
        temp=weather["temp_c"],
        humidity=weather["humidity"],
        condition=weather["condition"]["text"]
    )

@app.route("/weather")
def weather():
    params = {
        "key": WEATHER_API_KEY,
        "q": "Pune",
        "aqi": "yes"
    }
    r = requests.get(WEATHER_URL, params=params).json()
    return jsonify({
        "temp": r["current"]["temp_c"],
        "humidity": r["current"]["humidity"],
        "condition": r["current"]["condition"]["text"]
    })

@app.route("/live_data")
def live_data():
    data = generate_sensor_data()
    status = "Safe"

    if (data["PM2_5"] > THRESHOLDS["PM2_5"] or
        data["CO2"] > THRESHOLDS["CO2"] or
        data["Lead_Level"] > THRESHOLDS["Lead_Level"]):
        status = random.choice(["Warning", "Danger"])

    data["status"] = status
    sensor_history.append(data)
    return jsonify(data)

@app.route("/graphs")
def graphs():
    return render_template("Graphs.html")

@app.route("/download_report")
def download_report():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp","PM2.5","CO2","pH","Turbidity","Lead","Status"])

    for row in sensor_history:
        writer.writerow([
            row["timestamp"], row["PM2_5"], row["CO2"],
            row["pH"], row["Turbidity"], row["Lead_Level"], row["status"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=Environment_Report.csv"}
    )
if __name__ == "__main__":
    app.run(debug=True) 