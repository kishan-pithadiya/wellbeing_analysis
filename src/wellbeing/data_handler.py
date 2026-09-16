from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np
import pandas as pd


DEFAULT_WEIGHTS: Dict[str, float] = {
    "gdpPercap": 0.45,
    "lifeExp": 0.45,
    "pop_log_inv": 0.10,
}


@dataclass
class DevelopmentHandler:
    data_dir: str = "data"
    filename: str = "gapminder.csv"
    data: Optional[pd.DataFrame] = field(default=None, init=False, repr=False)

    def load_data(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, self.filename)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Could not find dataset at '{path}'. "
            )

        df = pd.read_csv(path)

        expected_cols = {"country", "year", "pop", "continent", "lifeExp", "gdpPercap"}
        missing = expected_cols - set(df.columns)
        if missing:
            raise ValueError(f"Dataset is missing expected columns: {missing}")

        df = df.drop_duplicates()
        df = df.dropna(subset=["country", "year", "pop", "lifeExp", "gdpPercap"])

        df["year"] = df["year"].astype(int)
        df["country"] = df["country"].astype(str).str.strip()

        self.data = df.reset_index(drop=True)
        return self.data

    @staticmethod
    def _min_max_normalize(series: pd.Series) -> pd.Series:
        lo, hi = series.min(), series.max()
        if hi == lo:
            return pd.Series(np.zeros(len(series)), index=series.index)
        return (series - lo) / (hi - lo)

    def compute_development_index(
        self, weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        if self.data is None:
            self.load_data()

        weights = weights or DEFAULT_WEIGHTS
        total_weight = sum(weights.values())
        if not np.isclose(total_weight, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

        df = self.data.copy()

        df["gdpPercap_log"] = np.log1p(df["gdpPercap"])
        df["pop_log"] = np.log1p(df["pop"])
        df["pop_log_inv"] = -df["pop_log"]

        norm_cols = {}
        for year, group in df.groupby("year"):
            idx = group.index
            norm_cols.setdefault("gdpPercap_norm", pd.Series(dtype=float))
            norm_cols.setdefault("lifeExp_norm", pd.Series(dtype=float))
            norm_cols.setdefault("pop_log_inv_norm", pd.Series(dtype=float))

            norm_cols["gdpPercap_norm"] = pd.concat(
                [norm_cols["gdpPercap_norm"], self._min_max_normalize(group["gdpPercap_log"])]
            )
            norm_cols["lifeExp_norm"] = pd.concat(
                [norm_cols["lifeExp_norm"], self._min_max_normalize(group["lifeExp"])]
            )
            norm_cols["pop_log_inv_norm"] = pd.concat(
                [norm_cols["pop_log_inv_norm"], self._min_max_normalize(group["pop_log_inv"])]
            )

        df["gdpPercap_norm"] = norm_cols["gdpPercap_norm"]
        df["lifeExp_norm"] = norm_cols["lifeExp_norm"]
        df["pop_log_inv_norm"] = norm_cols["pop_log_inv_norm"]

        df["development_index"] = (
            weights["gdpPercap"] * df["gdpPercap_norm"]
            + weights["lifeExp"] * df["lifeExp_norm"]
            + weights["pop_log_inv"] * df["pop_log_inv_norm"]
        ) * 100 

        self.data = df
        return self.data

    def get_top_countries(self, n: int = 10, year: Optional[int] = None) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]

        ranked = (
            subset.sort_values("development_index", ascending=False)
            .loc[:, ["country", "continent", "year", "gdpPercap", "lifeExp", "pop", "development_index"]]
            .reset_index(drop=True)
        )
        ranked.insert(0, "rank", ranked.index + 1)
        return ranked.head(n)

    def get_country_rank(self, country: str, year: Optional[int] = None) -> pd.DataFrame:

        ranked = self.get_top_countries(n=len(self.data["country"].unique()), year=year)
        match = ranked[ranked["country"].str.lower() == country.lower()]
        if match.empty:
            raise ValueError(f"Country '{country}' not found for the requested year.")
        return match

    def get_country_trend(self, country: str) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        subset = self.data[self.data["country"].str.lower() == country.lower()]
        if subset.empty:
            raise ValueError(f"Country '{country}' not found in the dataset.")
        return subset.sort_values("year").reset_index(drop=True)

    def compare_countries(self, countries: list) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        lowered = [c.lower() for c in countries]
        subset = self.data[self.data["country"].str.lower().isin(lowered)]
        found = set(subset["country"].str.lower().unique())
        missing = set(lowered) - found
        if missing:
            raise ValueError(f"Countries not found in dataset: {sorted(missing)}")
        return subset.sort_values(["country", "year"]).reset_index(drop=True)
    
    def get_continent_summary(self, year: Optional[int] = None) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]

        summary = (
            subset.groupby("continent")
            .agg(
                countries=("country", "nunique"),
                avg_gdpPercap=("gdpPercap", "mean"),
                avg_lifeExp=("lifeExp", "mean"),
                avg_development_index=("development_index", "mean"),
            )
            .sort_values("avg_development_index", ascending=False)
            .reset_index()
        )
        return summary

    def get_global_yearly_trend(self) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        return (
            self.data.groupby("year")["development_index"]
            .mean()
            .reset_index()
            .rename(columns={"development_index": "avg_development_index"})
        )

    def get_summary_statistics(self, year: Optional[int] = None) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        cols = ["gdpPercap", "lifeExp", "pop", "development_index"]
        return subset[cols].describe().round(2)

    def get_correlation_matrix(self, year: Optional[int] = None) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        cols = ["gdpPercap", "lifeExp", "pop", "development_index"]
        return subset[cols].corr().round(3)

    def get_biggest_movers(
        self, start_year: int, end_year: int, n: int = 10, ascending: bool = False
    ) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        years_available = set(self.data["year"].unique())
        for y in (start_year, end_year):
            if y not in years_available:
                raise ValueError(f"Year {y} not found in dataset. Available years: {sorted(years_available)}")

        start = self.data[self.data["year"] == start_year].set_index("country")["development_index"]
        end = self.data[self.data["year"] == end_year].set_index("country")["development_index"]

        change = (end - start).dropna().rename("change").reset_index()
        change[f"index_{start_year}"] = change["country"].map(start)
        change[f"index_{end_year}"] = change["country"].map(end)

        return change.sort_values("change", ascending=ascending).head(n).reset_index(drop=True)

    def get_percentage_change_leaders(
        self, start_year: int, end_year: int, n: int = 10, ascending: bool = False
    ) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        start = self.data[self.data["year"] == start_year].set_index("country")["development_index"]
        end = self.data[self.data["year"] == end_year].set_index("country")["development_index"]

        merged = pd.DataFrame({"start": start, "end": end}).dropna()
        merged["pct_change"] = ((merged["end"] - merged["start"]) / merged["start"]) * 100
        merged = merged.rename(
            columns={"start": f"index_{start_year}", "end": f"index_{end_year}"}
        ).reset_index()

        return merged.sort_values("pct_change", ascending=ascending).head(n).reset_index(drop=True)

    def get_extremes(self, column: str, year: Optional[int] = None) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in dataset.")

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]

        max_row = subset.loc[[subset[column].idxmax()]]
        min_row = subset.loc[[subset[column].idxmin()]]
        result = pd.concat([max_row, min_row]).reset_index(drop=True)
        result.insert(0, "extreme", ["max", "min"])
        return result[["extreme", "country", "continent", "year", column]]

    def filter_by_threshold(
        self, column: str, threshold: float, comparison: str = "greater", year: Optional[int] = None
    ) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        if column not in self.data.columns:
            raise ValueError(f"Column '{column}' not found in dataset.")

        ops = {
            "greater": lambda s: s > threshold,
            "greater_equal": lambda s: s >= threshold,
            "less": lambda s: s < threshold,
            "less_equal": lambda s: s <= threshold,
        }
        if comparison not in ops:
            raise ValueError(f"comparison must be one of {list(ops.keys())}")

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        mask = ops[comparison](subset[column])

        return (
            subset[mask]
            .sort_values(column, ascending=(comparison in ("less", "less_equal")))
            [["country", "continent", "year", column, "development_index"]]
            .reset_index(drop=True)
        )

    def get_decade_averages(self) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        df = self.data.copy()
        df["decade"] = (df["year"] // 10) * 10
        df["decade_label"] = df["decade"].astype(str) + "s"

        summary = (
            df.groupby("decade_label")
            .agg(
                avg_gdpPercap=("gdpPercap", "mean"),
                avg_lifeExp=("lifeExp", "mean"),
                avg_development_index=("development_index", "mean"),
                num_country_year_rows=("country", "count"),
            )
            .round(2)
        )

        summary = summary.reindex(sorted(summary.index, key=lambda s: int(s[:-1])))
        return summary.reset_index()

    def get_country_count_by_continent(self, year: Optional[int] = None) -> pd.Series:

        if self.data is None:
            self.load_data()

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        return subset.groupby("continent")["country"].nunique().sort_values(ascending=False)

    def get_gdp_quartile_analysis(self, year: Optional[int] = None) -> pd.DataFrame:

        if self.data is None or "development_index" not in self.data.columns:
            self.compute_development_index()

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year].copy()

        subset["gdp_quartile"] = pd.qcut(
            subset["gdpPercap"], q=4, labels=["Q1 (poorest)", "Q2", "Q3", "Q4 (richest)"]
        )

        summary = (
            subset.groupby("gdp_quartile", observed=True)
            .agg(
                countries=("country", "nunique"),
                avg_gdpPercap=("gdpPercap", "mean"),
                avg_lifeExp=("lifeExp", "mean"),
                avg_development_index=("development_index", "mean"),
            )
            .round(2)
            .reset_index()
        )
        return summary

    def get_data_quality_report(self) -> pd.DataFrame:

        if self.data is None:
            self.load_data()

        report = pd.DataFrame(
            {
                "dtype": self.data.dtypes.astype(str),
                "missing_values": self.data.isna().sum(),
                "missing_pct": (self.data.isna().mean() * 100).round(2),
                "unique_values": self.data.nunique(),
            }
        )
        report.index.name = "column"
        return report.reset_index()