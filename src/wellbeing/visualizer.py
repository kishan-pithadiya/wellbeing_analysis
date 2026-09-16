from __future__ import annotations

from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class DevelopmentVisualizer:
    def __init__(self, data: pd.DataFrame):
        if "development_index" not in data.columns:
            raise ValueError(
                "The provided data has no 'development_index' column. "
                "Call DevelopmentHandler.compute_development_index() first."
            )
        self.data = data

    def plot_top_countries(self, n: int = 20, year: Optional[int] = None, save_path: Optional[str] = None):

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        top = subset.sort_values("development_index", ascending=False).head(n)

        plt.figure(figsize=(10, max(6, n * 0.35)))
        plt.barh(top["country"][::-1], top["development_index"][::-1], color="#2E86AB")
        plt.xlabel("Development Index (0-100)")
        plt.title(f"Top {n} Countries by Development Index ({year})")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_correlation(self, x: str = "gdpPercap", y: str = "development_index",
                          year: Optional[int] = None, save_path: Optional[str] = None):

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]

        plt.figure(figsize=(8, 6))
        plt.scatter(subset[x], subset[y], alpha=0.6, c="#A23B72")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"{y} vs {x} ({year})")
        if x == "gdpPercap":
            plt.xscale("log")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_trend(self, country: str, save_path: Optional[str] = None):

        subset = self.data[self.data["country"].str.lower() == country.lower()].sort_values("year")
        if subset.empty:
            raise ValueError(f"Country '{country}' not found in the dataset.")

        plt.figure(figsize=(8, 5))
        plt.plot(subset["year"], subset["development_index"], marker="o", color="#F18F01")
        plt.xlabel("Year")
        plt.ylabel("Development Index")
        plt.title(f"Development Index Trend: {country} (1952-2007)")
        plt.grid(alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_multi_country_trend(self, countries: List[str], save_path: Optional[str] = None):

        plt.figure(figsize=(9, 6))
        for country in countries:
            subset = self.data[self.data["country"].str.lower() == country.lower()].sort_values("year")
            if subset.empty:
                raise ValueError(f"Country '{country}' not found in the dataset.")
            plt.plot(subset["year"], subset["development_index"], marker="o", label=country)

        plt.xlabel("Year")
        plt.ylabel("Development Index")
        plt.title("Development Index Trend Comparison")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_continent_comparison(self, year: Optional[int] = None, save_path: Optional[str] = None):

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        continent_avg = (
            subset.groupby("continent")["development_index"]
            .mean()
            .sort_values(ascending=False)
        )

        plt.figure(figsize=(8, 5))
        sns.barplot(x=continent_avg.values, y=continent_avg.index, hue=continent_avg.index,
                    palette="viridis", legend=False)
        plt.xlabel("Average Development Index")
        plt.title(f"Average Development Index by Continent ({year})")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_boxplot_by_continent(self, year: Optional[int] = None, save_path: Optional[str] = None):

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]

        plt.figure(figsize=(9, 6))
        order = (
            subset.groupby("continent")["development_index"]
            .median()
            .sort_values(ascending=False)
            .index
        )
        sns.boxplot(x="continent", y="development_index", data=subset, order=order,
                    hue="continent", palette="coolwarm", legend=False)
        plt.xlabel("Continent")
        plt.ylabel("Development Index")
        plt.title(f"Development Index Spread by Continent ({year})")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_distribution(self, year: Optional[int] = None, save_path: Optional[str] = None):

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]

        plt.figure(figsize=(8, 5))
        sns.histplot(subset["development_index"], bins=20, kde=True, color="#2E86AB")
        plt.xlabel("Development Index")
        plt.ylabel("Number of Countries")
        plt.title(f"Distribution of Development Index Across Countries ({year})")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_correlation_heatmap(self, year: Optional[int] = None, save_path: Optional[str] = None):

        year = year or int(self.data["year"].max())
        subset = self.data[self.data["year"] == year]
        cols = ["gdpPercap", "lifeExp", "pop", "development_index"]
        corr = subset[cols].corr()

        plt.figure(figsize=(7, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
        plt.title(f"Correlation Heatmap ({year})")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_global_trend(self, save_path: Optional[str] = None):

        global_trend = self.data.groupby("year")["development_index"].mean()

        plt.figure(figsize=(8, 5))
        plt.plot(global_trend.index, global_trend.values, marker="o", color="#3B1F2B")
        plt.xlabel("Year")
        plt.ylabel("Average Development Index")
        plt.title("Global Average Development Index Over Time (1952-2007)")
        plt.grid(alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_biggest_movers(
        self, start_year: int, end_year: int, n: int = 10, ascending: bool = False,
        save_path: Optional[str] = None,
    ):

        start = self.data[self.data["year"] == start_year].set_index("country")["development_index"]
        end = self.data[self.data["year"] == end_year].set_index("country")["development_index"]
        change = (end - start).dropna().sort_values(ascending=ascending).head(n)

        label = "Decliners" if ascending else "Gainers"
        colors = "#C1121F" if ascending else "#2E7D32"

        plt.figure(figsize=(10, max(6, n * 0.35)))
        plt.barh(change.index[::-1], change.values[::-1], color=colors)
        plt.xlabel(f"Change in Development Index ({start_year} \u2192 {end_year})")
        plt.title(f"Top {n} {label}: Development Index Change {start_year}\u2013{end_year}")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()