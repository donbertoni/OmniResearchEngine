import pandas as pd


def fmt_num(val, dec: int = 2) -> str:
    if val is None or pd.isna(val) or val == 0.0:
        return "--"
    s = f"{val:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(val) -> str:
    if val is None or pd.isna(val):
        return "0,00%"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%".replace(".", ",")
