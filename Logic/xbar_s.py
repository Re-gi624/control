# logic/xbar_s.py
import numpy as np
import pandas as pd

# Tabla c4 para tamaño de subgrupo n (2–25 aprox)
C4_TABLE = {
    2: 0.797884,
    3: 0.886227,
    4: 0.921317,
    5: 0.940946,
    6: 0.951533,
    7: 0.958672,
    8: 0.963907,
    9: 0.967907,
    10: 0.971033,
    11: 0.973555,
    12: 0.975662,
    13: 0.977450,
    14: 0.978996,
    15: 0.980359,
    16: 0.981578,
    17: 0.982682,
    18: 0.983697,
    19: 0.984640,
    20: 0.985521,
    21: 0.986350,
    22: 0.987134,
    23: 0.987878,
    24: 0.988588,
    25: 0.989269,
}


def _get_c4(n: int) -> float:
    if n not in C4_TABLE:
        raise ValueError(f"n = {n} fuera de rango para c4 (soportado 2–25).")
    return C4_TABLE[n]


def xbar_s_analysis(df_numeric: pd.DataFrame):
    """
    Análisis X̄–S con subgrupos.
    df_numeric: DataFrame SOLO con columnas numéricas.
                Cada fila = un subgrupo, cada columna = mediciones del subgrupo.

    Devuelve dict con:
        - n, c4
        - subgroups (índices)
        - xbar_i, s_i
        - xbarbar, sbar
        - límites UCL/CL/LCL para X y S
        - summary (DataFrame de métricas)
        - detail  (DataFrame por subgrupo)
    """

    if df_numeric is None or df_numeric.empty:
        raise ValueError("No hay datos numéricos para X̄–S.")

    # Asegurar formato numérico
    X = df_numeric.to_numpy(dtype=float)

    m, n = X.shape  # m = subgrupos, n = tamaño de subgrupo
    if n < 2:
        raise ValueError("Se requieren al menos 2 columnas (tamaño de subgrupo >= 2).")

    c4 = _get_c4(n)

    # Medias y desviaciones por subgrupo
    xbar_i = X.mean(axis=1)
    s_i = X.std(axis=1, ddof=1)

    # Promedios globales
    xbarbar = xbar_i.mean()
    sbar = s_i.mean()

    # Límites X̄ (fórmulas de tu maestra)
    ucl_x = xbarbar + 3 * sbar / (c4 * np.sqrt(n))
    lcl_x = xbarbar - 3 * sbar / (c4 * np.sqrt(n))
    cl_x = xbarbar

    # Límites S (fórmulas de tu maestra)
    term = (sbar / c4) * np.sqrt(1 - c4 ** 2)
    ucl_s = sbar + 3 * term
    lcl_s = sbar - 3 * term
    cl_s = sbar
    if lcl_s < 0:
        lcl_s = 0.0  # por seguridad, la desviación no puede ser negativa

    subgroups = np.arange(1, m + 1)

    # Tabla resumen
    summary = pd.DataFrame({
        "Métrica": [
            "n (tamaño de subgrupo)",
            "Número de subgrupos (m)",
            "c4",
            "X̄̄ (promedio de medias)",
            "S̄ (promedio de S)",
            "UCL_X",
            "CL_X",
            "LCL_X",
            "UCL_S",
            "CL_S",
            "LCL_S",
        ],
        "Valor": [
            n,
            m,
            c4,
            xbarbar,
            sbar,
            ucl_x,
            cl_x,
            lcl_x,
            ucl_s,
            cl_s,
            lcl_s,
        ]
    })

    # Tabla por subgrupo
    detail = pd.DataFrame({
        "Subgrupo": subgroups,
        "Media (X̄_i)": xbar_i,
        "S_i": s_i,
    })

    return {
        "n": n,
        "m": m,
        "c4": c4,
        "subgroups": subgroups,
        "xbar_i": xbar_i,
        "s_i": s_i,
        "xbarbar": xbarbar,
        "sbar": sbar,
        "ucl_x": ucl_x,
        "cl_x": cl_x,
        "lcl_x": lcl_x,
        "ucl_s": ucl_s,
        "cl_s": cl_s,
        "lcl_s": lcl_s,
        "summary": summary,
        "detail": detail,
    }
