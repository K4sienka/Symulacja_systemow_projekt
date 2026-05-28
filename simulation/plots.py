from pathlib import Path

import matplotlib.pyplot as plt

from config import RESULTS_DIR, PLOT_PATH, SCENARIO_NAME


def show_plot(history):
    Path(RESULTS_DIR).mkdir(exist_ok=True)

    plt.figure(figsize=(10, 6))

    plt.plot(history["S"], label="Podatni (S)")
    plt.plot(history["I"], label="Zakażeni (I)")
    plt.plot(history["R"], label="Ozdrowiali (R)")

    plt.xlabel("Krok symulacji")
    plt.ylabel("Liczba osób")
    plt.title(f"Przebieg epidemii w modelu SIR - {SCENARIO_NAME}")
    plt.legend()
    plt.grid(True)

    plt.savefig(PLOT_PATH, dpi=300, bbox_inches="tight")
    plt.close()