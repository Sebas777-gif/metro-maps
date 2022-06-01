import tkinter as tk
import main


SCALE = 200


def calculate_layout():
    err_label["text"] = ""
    err_label["fg"] = "red"
    try:
        GRIDS = int(ent_grids.get())
        SEARCH_RADIUS = int(ent_radius.get())
        BEND_FACTOR = int(ent_bend.get())
        GEO_PENALTY = int(ent_geo.get())
        if GRIDS <= 0:
            err_label["text"] = "Fehler: Anzahl Zellen muss größer 0 sein."
            return
        if SEARCH_RADIUS < 0:
            err_label["text"] = "Fehler: Suchradius darf nicht negativ sein."
            return
        if BEND_FACTOR < 0 or GEO_PENALTY < 0:
            err_label["text"] = "Fehler: Faktoren dürfen nicht negativ sein."
            return
        if SEARCH_RADIUS > 10:
            err_label["text"]\
                = "Warnung: Gewählter Suchradius ist sehr groß. Funktionalität kann nicht garantiert werden."
            err_label["fg"] = "yellow"
        main.main(GRIDS, SCALE, SEARCH_RADIUS, BEND_FACTOR, GEO_PENALTY)
    except ValueError:
        if not (ent_grids.get() and ent_radius.get() and ent_bend.get() and ent_geo.get()):
            err_label["text"] = "Fehler: Bitte alle Werte ausfüllen."
        else:
            err_label["text"] = "Fehler: Alle Werte müssen ganzzahlig sein."


window = tk.Tk()
window.title("Liniennetzplangenerierung")

ent_grids = tk.Entry(master=window, width=3)
lbl_grids = tk.Label(master=window, text="Zellen")
ent_radius = tk.Entry(master=window, width=3)
lbl_radius = tk.Label(master=window, text="Suchradius")
ent_bend = tk.Entry(master=window, width=3)
lbl_bend = tk.Label(master=window, text="Knick-Faktor")
ent_geo = tk.Entry(master=window, width=3)
lbl_geo = tk.Label(master=window, text="Geo-Faktor")

err_label = tk.Label(master=window, text="", fg="red")

ent_grids.grid(row=0, column=0, sticky="e", padx=5, pady=(5,0))
lbl_grids.grid(row=0, column=1, sticky="w", pady=(5,0))
ent_radius.grid(row=1, column=0, sticky="e", padx=5)
lbl_radius.grid(row=1, column=1, sticky="w")
ent_bend.grid(row=2, column=0, sticky="e", padx=5)
lbl_bend.grid(row=2, column=1, sticky="w")
ent_geo.grid(row=3, column=0, sticky="e", padx=5)
lbl_geo.grid(row=3, column=1, sticky="w")

err_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=5)

btn_calculate = tk.Button(
    master=window,
    text="Berechne Layout",
    command=calculate_layout
)
btn_calculate.grid(row=5, column=2, sticky="e", padx=5, pady=5)

for i in range(6):
    window.rowconfigure(i, weight=1, minsize=30)
for j in range(3):
    window.columnconfigure(j, weight=1, minsize=50)

window.mainloop()


