# logic/mean_sd.py
import numpy as np
import pandas as pd
from scipy.stats import norm


# ==========================================================
# CÁLCULO PRINCIPAL (TABLA)
# ==========================================================

def mean_sd_stats(x):
    """
    Dado un arreglo de valores numéricos x,
    calcula estadísticas Mean-SD y límites ±3σ.

    Retorna:
        DataFrame con todos los resultados
    """

    x = np.asarray(x, dtype=float)

    if x.size < 2:
        raise ValueError("Se requieren al menos 2 datos.")
    if np.isnan(x).any():
        raise ValueError("Los datos contienen valores NaN.")

    media = x.mean()
    s = x.std(ddof=1)  # desviación estándar muestral
    LCL = media - 3 * s
    UCL = media + 3 * s

    stats = {
        "Métrica": [
            "n (tamaño de muestra)",
            "Media",
            "DesvEst (s muestral)",
            "Mínimo",
            "Q1 (25%)",
            "Mediana",
            "Q3 (75%)",
            "Máximo",
            "LCL = media - 3s",
            "UCL = media + 3s"
        ],
        "Valor": [
            int(len(x)),
            float(media),
            float(s),
            float(np.min(x)),
            float(np.percentile(x, 25)),
            float(np.median(x)),
            float(np.percentile(x, 75)),
            float(np.max(x)),
            float(LCL),
            float(UCL)
        ]
    }

    return pd.DataFrame(stats)


# ==========================================================
# GRÁFICA 1: CONTROL CHART MEAN-SD (SERIE DE DATOS)
# ==========================================================

def plot_meansd_series(ax, x):
    """
    Dibuja gráfico de control (media y límites ±3σ).
    """
    x = np.asarray(x, dtype=float)

    media = x.mean()
    s = x.std(ddof=1)

    LCL = media - 3 * s
    UCL = media + 3 * s

    idx = np.arange(1, len(x) + 1)

    # Plot serie
    ax.plot(idx, x, marker='o', linestyle='-', color='blue', label="Datos")

    # Líneas horizontales
    ax.axhline(media, color='green', linestyle='--', label=f"Media = {media:.3f}")
    ax.axhline(UCL, color='red', linestyle='--', label=f"Límite superior (+3σ)")
    ax.axhline(LCL, color='red', linestyle='--', label=f"Límite inferior (-3σ)")

    ax.set_title("Gráfico de Control (Mean-SD)")
    ax.set_xlabel("Muestra")
    ax.set_ylabel("Valor")
    ax.grid(True)
    ax.legend()


# ==========================================================
# GRÁFICA 2: HISTOGRAMA + CURVA NORMAL AJUSTADA
# ==========================================================

def plot_hist(ax, x):
    """
    Histograma con curva normal ajustada.
    """
    x = np.asarray(x, dtype=float)

    media = x.mean()
    s = x.std(ddof=1)

    # Histograma
    ax.hist(x, bins='auto', density=True, alpha=0.7, color='skyblue')

    # Rango para curva normal
    xs = np.linspace(np.min(x), np.max(x), 200)
    pdf = norm.pdf(xs, media, s)

    ax.plot(xs, pdf, 'r--', label="Curva Normal")

    ax.set_title("Histograma y Normal Ajustada")
    ax.set_xlabel("Valor")
    ax.set_ylabel("Densidad")
    ax.grid(True)
    ax.legend()
