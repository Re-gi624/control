# logic/schilling.py
import math
import numpy as np
import pandas as pd


# ===========================================================
# TABLA 12.15 – Valores para calcular n en planes PDTL con c = 0
# ===========================================================

# f de fila (parte “gruesa” del f total)
F_BASE = np.array([
    0.90, 0.80, 0.70, 0.60, 0.50,
    0.40, 0.30, 0.20, 0.10, 0.00
])

# Encabezados de columna (parte “fina” del f total)
F_COL = np.array([
    0.00, 0.01, 0.02, 0.03, 0.04,
    0.05, 0.06, 0.07, 0.08, 0.09
])

# Matriz K correspondiente a cada combinación f_base + f_col
# (MATRIZ COMPLETA RECONSTRUIDA DE TU TABLA)
K_TABLE = np.array([
    [1.0000, 0.9562, 0.9117, 0.8659, 0.8184, 0.7686, 0.7153, 0.6567, 0.5886, 0.5000],
    [1.4307, 1.3865, 1.3428, 1.2995, 1.2565, 1.2137, 1.1711, 1.1286, 1.0860, 1.0432],
    [1.9125, 1.8601, 1.8088, 1.7586, 1.7093, 1.6610, 1.6135, 1.5667, 1.5207, 1.4754],
    [2.5129, 2.4454, 2.3797, 2.3159, 2.2538, 2.1933, 2.1344, 2.0769, 2.0208, 1.9660],
    [3.3219, 3.2278, 3.1372, 3.0497, 2.9652, 2.8836, 2.8047, 2.7283, 2.6543, 2.5825],
    [4.5076, 4.3640, 4.2270, 4.0963, 3.9715, 3.8515, 3.7368, 3.6268, 3.5212, 3.4169],
    [6.4557, 6.2054, 5.9705, 5.7496, 5.5415, 5.3451, 5.1594, 4.9836, 4.8168, 4.6583],
    [10.3189, 9.7682, 9.2674, 8.8099, 8.3902, 8.0039, 7.6471, 7.3165, 7.0093, 6.7231],
    [21.8543, 19.7589, 18.0124, 16.5342, 15.2668, 14.1681, 13.2064, 12.3576, 11.6028, 10.9272],
    [np.nan, 229.1053, 113.9741, 75.5957, 56.4055, 44.8906, 37.2133, 31.7289, 27.6150, 24.4149]
])


# ===========================================================
# FUNCIÓN PARA BUSCAR EL F MÁS CERCANO EN LA TABLA
# ===========================================================

def _nearest_f_from_K(K: float):
    """
    Encuentra en la tabla 12.15 la fila y columna cuyos valores K estén
    más cerca del K calculado (N * LTPD).

    Devuelve:
        f_total, f_fila, f_col, K_tabla, row_idx, col_idx
    """

    # Diferencias absolutas
    diffs = np.abs(K_TABLE - K)

    # Ignorar el NaN (primera columna, última fila)
    diffs = np.where(np.isnan(K_TABLE), np.inf, diffs)

    # Índice del valor más cercano
    idx = np.argmin(diffs)
    row, col = np.unravel_index(idx, diffs.shape)

    f_fila = float(F_BASE[row])
    f_col = float(F_COL[col])
    f_total = f_fila + f_col
    K_tabla = float(K_TABLE[row, col])

    return f_total, f_fila, f_col, K_tabla, row, col


# ===========================================================
# FUNCIÓN PRINCIPAL DEL ANÁLISIS SCHILLING
# ===========================================================

def calculate_schilling_plan(N: int, ltpd: float):
    """
    Calcula el plan PDTL (c = 0) usando la TABLA 12.15.

    Entradas:
        N    : tamaño del lote
        ltpd : valor de LTPD en proporción (ej. 0.025)

    Salidas:
        dict con resultados y un DataFrame para mostrar en tabla
    """

    if N <= 0:
        raise ValueError("N debe ser mayor que 0.")
    if ltpd <= 0:
        raise ValueError("LTPD debe ser mayor que 0.")

    # Paso 1 — Calcular K
    K = N * ltpd

    # Paso 2 — Buscar el valor K más cercano en la tabla
    f_total, f_fila, f_col, K_tabla, row_idx, col_idx = _nearest_f_from_K(K)

    # Paso 3 — Calcular tamaño de muestra
    n_raw = f_total * N
    n_final = math.ceil(n_raw)     # Se redondea hacia arriba

    # Convertir a DataFrame para desplegar
    df_result = pd.DataFrame({
        "Parámetro": [
            "N (tamaño de lote)",
            "LTPD",
            "K = N * LTPD",
            "f_fila",
            "f_col",
            "f_total (f_fila + f_col)",
            "K_tabla (valor más cercano)",
            "n calculado (sin redondear)",
            "n final (redondeado hacia arriba)",
            "c (número de aceptación)"
        ],
        "Valor": [
            N,
            ltpd,
            K,
            f_fila,
            f_col,
            f_total,
            K_tabla,
            n_raw,
            n_final,
            0
        ]
    })

    return {
        "N": N,
        "LTPD": ltpd,
        "K": K,
        "f_total": f_total,
        "f_fila": f_fila,
        "f_col": f_col,
        "K_tabla": K_tabla,
        "n_raw": n_raw,
        "n_final": n_final,
        "row_index": row_idx,
        "col_index": col_idx,
        "table": df_result
    }


# ===========================================================
# CASO ESPECIAL: TAMAÑO DE LOTE INFINITO (nota de la tabla)
# ===========================================================

def schilling_infinite_lot(ltpd: float):
    """
    Caso especial: para tamaño infinito de lote,
    n = 2.303 / p_L.
    """
    if ltpd <= 0:
        raise ValueError("LTPD debe ser mayor que 0.")

    n_raw = 2.303 / ltpd
    n_final = math.ceil(n_raw)

    return n_final, n_raw
