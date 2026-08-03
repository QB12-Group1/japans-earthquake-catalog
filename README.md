# 🌏 Japan Earthquake Catalog Analysis

An automated pipeline to collect, process, and analyze earthquake data for the Japan region from multiple international sources. Designed for reproducibility, data integrity, and insightful geological analysis.

---

## 🏗️ Architecture

The project follows a modular ETL (Extract, Transform, Load) architecture:

* `src/collectors/`: Fetches raw data from seismic networks (USGS, GEOFON, EMSC).
* `src/transform/`: Cleans, standardizes, and merges heterogeneous datasets.
* `src/database/`: Manages PostgreSQL connection, schema definitions, and data insertion.
* `sql/analysis/`: Contains SQL scripts for dangerous earthquake identification and monthly statistics.

---

## 🗃️ Data Sources

This project aggregates data from the following global seismic networks:

* **USGS** (United States Geological Survey)
* **GEOFON** (GFZ German Research Centre for Geosciences)
* **EMSC** (European-Mediterranean Seismological Centre)
* **Side Dataset** (Secondary/Supplemental seismic records)

---

## 🚀 Key Features

* **Multi-Source Integration:** Normalizes data formats from various seismological providers.
* **Automated Pipeline:** Full end-to-end processing from raw CSVs to ready-to-analyze SQL outputs.
* **SQL-Driven Analysis:** Pre-built queries for calculating monthly earthquake trends and identifying dangerous events.
* **Data Integrity:** Robust transformation layer ensuring consistent coordinate and magnitude formatting.

---

## ⚙️ Prerequisites

* Python 3.10+
* PostgreSQL
* `uv` (Recommended for dependency management)

---

## 🛠️ Running the Project

### 1. Installation
Clone the repository and install dependencies using `uv`:

```bash
uv sync
```

### 2. Configuration
Copy the environment template and set your database credentials:

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Execution
Run the main pipeline to process data:

```bash
uv run main.py
```

### 4. Running Tests
Ensure data integrity by running the test suite:

```bash
uv run -m unittest discover tests
```

---

## 📊 Available Analyses

You can execute the pre-built analysis scripts directly against the database:

* **Dangerous Quakes:** `sql/analysis/dangerous_quakes.sql` (Finds high-magnitude/shallow events).
* **Monthly Stats:** `sql/analysis/monthly_stats.sql` (Aggregates activity over time).

---

## 📚 Contributing

We welcome contributions! Please follow the standard Git workflow:

1. **Branching:** Create a feature branch.
2. **Commit:** Follow semantic commit messages.
3. **Pull Request:** Submit to `dev` for review before merging into `main`.

See `CONTRIBUTING.md` for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
