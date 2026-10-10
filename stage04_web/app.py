from flask import Flask, jsonify, render_template, send_from_directory, abort, Response
import os

app = Flask(__name__)

# The flag is read from an environment variable (kept private).
# The default is only for testing.
FLAG = os.environ.get("EC04_FLAG", "ECORP{test_flag_change_me}")

# ---- Fake data (all fictional) ----
EMPLOYEES = {
    1001: {"id": 1001, "name": "R. Perera", "dept": "Finance", "incidents": []},
    1042: {"id": 1042, "name": "Night Shift Operator", "dept": "IT Operations", "incidents": [774]},
    1077: {"id": 1077, "name": "K. Silva", "dept": "HR", "incidents": [701]},
}

INCIDENTS = {
    701: {"id": 701, "title": "Printer offline", "status": "closed"},
    774: {
        "id": 774,
        "title": "Unusual outbound data transfer",
        "status": "open",
        "assigned_to": 1042,
        "evidence": "/evidence/network_capture.pcap",
        "flag": FLAG,
    },
}

BACKUP_TEXT = """# E Corp Employee Portal - config backup (DO NOT DEPLOY)
APP_ENV=staging
EMPLOYEE_ENDPOINT=/api/employees/<id>
INCIDENT_ENDPOINT=/api/incidents/<id>
# TODO: add authentication to the API before go-live
"""

# ---- Routes (web addresses) ----
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /backup/\n", mimetype="text/plain")

@app.route("/backup/")
def backup_index():
    #misconfiguration: the server lists the folder's contents
    return Response('<h1>Index of /backup/</h1><ul>'
                    '<li><a href="/backup/config.bak">config.bak</a></li></ul>',
                    mimetype="text/html")

@app.route("/backup/config.bak")
def backup():
    return Response(BACKUP_TEXT, mimetype="text/plain")

@app.route("/api/employees/<int:emp_id>")
def employee(emp_id):
    if emp_id not in EMPLOYEES:
        abort(404)
    return jsonify(EMPLOYEES[emp_id])

@app.route("/api/incidents/<int:inc_id>")
def incident(inc_id):
    if inc_id not in INCIDENTS:
        abort(404)
    return jsonify(INCIDENTS[inc_id])

@app.route("/evidence/<path:filename>")
def evidence(filename):
    return send_from_directory("evidence", filename, as_attachment=True)

if __name__ == "__main__":
    # debug=False is important for safety (from your risk table)
    app.run(host="0.0.0.0", port=8080, debug=False)

