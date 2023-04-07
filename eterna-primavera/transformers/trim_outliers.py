import pandas as pd


def trim_outliers(s: pd.Series, min: float = 0.05, max: float = 0.95) -> pd.Series:
    """Returns a series with outliers turned into NA."""
    return s.where((s > s.quantile(min)) & (s < s.quantile(max)), pd.NA)