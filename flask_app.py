from flask import Flask, redirect, url_for, request, render_template
from cluster import *

app = Flask(__name__)


@app.route("/success/<circuit>/<crew_number>/<hours>")
def success(circuit, crew_number, hours):
    hours = float(hours)
    crew_number = int(crew_number)
    sites = cluster_sites(hours)
    final = (sites[x] for x in range(0, crew_number))
    return final


@app.route("/enter", methods=["POST", "GET"])
def enter():
    if request.method == "POST":
        circuit = request.form["circuit"]
        crew_number = request.form["crew_number"]
        hours = request.form["hours"]
        return redirect(
            url_for("success", circuit=circuit, crew_number=crew_number, hours=hours)
        )
    else:
        return render_template("enter.html")


@app.route("/")
def index():
    return render_template("enter.html")


if __name__ == "__main__":
    app.run(debug=True)
