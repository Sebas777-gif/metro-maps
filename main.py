from flask import Flask, render_template, request
from calculations import calculate
from plotting import plot_graph


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


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
    params = plot_graph(grids, geo_penalty, bend_factor, search_radius)
    return render_template("layout.html", data=params)


if __name__ == "__main__":
    app.run()