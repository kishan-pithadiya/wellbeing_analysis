# 🌍 Global Development Index Analysis (Gapminder, 1952–2007)

## 📖 Introduction

This project analyzes the **Gapminder** dataset, which tracks population,
life expectancy, and GDP per capita for 142 countries every 5 years from
1952 to 2007. Instead of looking at any single raw indicator on its own,
the project computes a custom **Development Index**: a weighted
combination of GDP per capita, life expectancy, and (log-scaled, inverted)
population, so countries can be ranked and compared on a single 0–100
scale.

## 📌 Problem Statement

Raw indicators like GDP per capita or life expectancy each tell only part
of the story. This project builds a **Development Index** using these
weighted factors:

| Factor                         | Weight |
| ------------------------------- | ------ |
| GDP per capita (log-scaled)     | 0.45   |
| Life expectancy                 | 0.45   |
| Population (log-scaled, inverse)| 0.10   |

Normalization is done **within each year**, so countries are always
compared against their peers at that point in time rather than against
the full 1952–2007 range at once. Weights are configurable, any custom
`weights` dict summing to 1.0 can be passed to `compute_development_index`.

## 📊 Dataset

- Source: the public **[Gapminder](https://www.gapminder.org/data/)**
  dataset (five-year interval version).
- Covers **1952–2007** in 5-year steps, 142 countries.
- Columns: `country`, `year`, `pop`, `continent`, `lifeExp`, `gdpPercap`.
- Combined as a single CSV: `data/gapminder.csv` (merged from Gapminder's separate life expectancy, GDP per capita, and population indicator files).

## ⚙️ Project Structure

```
wellbeing_analysis/
├── data/
│   └── gapminder.csv                 # Gapminder dataset (1952-2007)
├── images/                           # Saved charts
├── notebooks/
│   ├── analysis.ipynb                 # Main analysis notebook (run locally, from a cloned folder)
│   └── analysis_colab.ipynb           # Same analysis, set up to run standalone in Google Colab
├── src/
│   └── wellbeing/                    # Python package
│       ├── __init__.py
│       ├── data_handler.py           # DevelopmentHandler
│       └── visualizer.py             # DevelopmentVisualizer
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── LICENSE.txt
└── README.md
```

## 🔧 Features & Functionality

- **Data Handling (`DevelopmentHandler`)**
  - Load and clean the Gapminder dataset
  - Compute the weighted Development Index (per year, with configurable weights)
  - Rank countries and fetch the top N for any year
  - Look up a specific country's rank/score, or compare several countries at once
  - Get a country's full time series (1952–2007)
  - Continent-level summaries (average GDP per capita, life expectancy, Development Index)
  - Global yearly trend (average Development Index across all countries, per year)
  - Descriptive statistics and a correlation matrix for the key indicators
  - Data-quality report (missing values, dtypes, unique counts)
  - "Biggest movers": countries with the largest Development Index gain or decline between any two years, by absolute change or percentage change
  - Country counts per continent, GDP-per-capita quartile analysis
  - Extremes lookup (max/min country for any column) and threshold filtering (e.g. all countries with life expectancy above 80)
  - Decade-level averages (1950s–2000s)

- **Visualization (`DevelopmentVisualizer`)**
  - Bar chart of the top N countries by Development Index
  - Scatter plot exploring correlations (e.g. GDP per capita vs. Development Index)
  - Correlation heatmap across GDP per capita, life expectancy, population, and the index
  - Line chart of a single country's Development Index over time
  - Multi-country comparison line chart
  - Continent comparison bar chart and boxplot (spread within each continent)
  - Histogram/KDE of the Development Index distribution across countries
  - Global average Development Index trend line (1952–2007)
  - Bar chart of the biggest gainers/decliners between two years

## 🚀 How to Run the Project

You can run the project in two ways:

### ☁️ Option A — Google Colab (recommended for a quick start)

- Open the notebook: `notebooks/analysis_colab.ipynb`.
- The notebook guides you through:
  - Uploading & unzipping `wellbeing_analysis.zip` (contains `src/wellbeing` and `data`).
  - Running the analysis end-to-end.
  - Generating rankings, trends, and visualizations.

### 💻 Option B — Local Machine (VS Code / PyCharm)

1. Clone or download this repo:

   ```bash
   git clone https://github.com/kishan-pithadiya/wellbeing_analysis.git
   cd wellbeing_analysis   ## to ensure path is correctly defined
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Open `notebooks/analysis.ipynb` in Jupyter, VS Code, or PyCharm and run all cells.
   Make sure `data/gapminder.csv` and `src/wellbeing/` are present (they're
   included in this repo).

### ⚡ Quick usage example

```python
import sys
sys.path.insert(0, "src")

from wellbeing import DevelopmentHandler, DevelopmentVisualizer

# Load & score
dh = DevelopmentHandler(data_dir="data")
dh.load_data()
dh.compute_development_index()

# Top 10 countries in 2007
print(dh.get_top_countries(n=10, year=2007))

# Visualize
dv = DevelopmentVisualizer(dh.data)
dv.plot_top_countries(n=20, year=2007)
dv.plot_correlation(x="gdpPercap", y="development_index", year=2007)
dv.plot_trend("Germany")
dv.plot_multi_country_trend(["Germany", "India", "Nigeria"])
dv.plot_continent_comparison(year=2007)
dv.plot_boxplot_by_continent(year=2007)
dv.plot_distribution(year=2007)
dv.plot_correlation_heatmap(year=2007)
dv.plot_global_trend()
dv.plot_biggest_movers(1952, 2007, n=10)               # biggest gainers
dv.plot_biggest_movers(1952, 2007, n=10, ascending=True)  # biggest decliners
```

## 📊 Interpreting the Results

- **Higher Development Index** values indicate a country scores well
  across economic strength (GDP per capita), health/human development
  (life expectancy), and is not being purely driven by population size.
- **Trend plots** show how a country's overall development has evolved
  across the 1952–2007 span useful for spotting long-run growth,
  stagnation, or setbacks.
- **Correlation plots** show how strongly GDP per capita and the
  Development Index move together within a given year.

## ⚠️ Assumptions & Limitations

- **Weights are heuristic**: the default weights reflect an assumed
  importance of each factor, they are not learned from data, and can be
  changed freely via the `weights` argument.
- **Normalization is year-relative**: a country's index is only
  comparable to other countries *in the same year*, not across years,
  since normalization bounds shift per year.
- **Dataset coverage**: limited to the 142 countries and 5-year
  snapshots (1952–2007) included in the Gapminder dataset, no data after 2007.

## 📑 Credits

- **Data**: [Gapminder](https://www.gapminder.org/data/)
- **License**: see `LICENSE.txt`.

## 📜 License

MIT License: see `LICENSE.txt` for details.
