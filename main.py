import json

from flask import Flask, render_template, request
from calculations import calculate
from plotting import plot_graph


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")


@app.route("/handle_data", methods=['POST'])
def handle_data():
    grids = int(request.form['grids'])
    geo_penalty = int(request.form['geo'])
    bend_factor = int(request.form['bend'])
    search_radius = int(request.form['radius'])
    calculate(grids, search_radius, bend_factor, geo_penalty)
    return render_template("index.html")


@app.route("/display_layout", methods=['POST'])
def display_layout():
    grids = int(request.form['grids'])
    geo_penalty = int(request.form['geo'])
    bend_factor = int(request.form['bend'])
    search_radius = int(request.form['radius'])
    try:
        with open('grid_graph_s' + str(search_radius) + 'gr' + str(grids) + 'b' + str(bend_factor)
                  + 'geo' + str(geo_penalty) + "params.json", 'r') as json_file:
            params = json.load(json_file)
    except FileNotFoundError :
        params = plot_graph(grids, geo_penalty, bend_factor, search_radius)

    return render_template("layout.html", data=params)


if __name__ == "__main__":
    app.run()
