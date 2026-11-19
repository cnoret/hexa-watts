# Hexa Watts: Energy Consumption Prediction Application

## 🔁 Overview

**Hexa Watts** is a Streamlit-based web application that allows users to analyze and predict electricity consumption across French regions. The app provides visualizations, exploratory data analysis (EDA), and machine learning predictions to support energy management and planning.

> **Note**: The application's interface and explanatory text are in French. This is to provide a localized experience for French-speaking users.

---

## 🎯 Features

1. **Data Visualization**:
   - Regional energy production and consumption trends.
   - Renewable energy production breakdown (solar, wind, hydro, bioenergy).
   - European energy comparisons using Eurostat data.

2. **Machine Learning**:
   - Predicts electricity consumption (in MW) based on region, date, time, and temperature data.
   - Gradient boosting model (`HistGradientBoostingRegressor`) trained on half-hourly regional consumption joined with daily regional temperatures (2016 to 2021).
   - Evaluated on the last twelve months of data (November 2020 to October 2021), which the model never sees during training. The app shows these test metrics (MAE, RMSE, R², relative error) next to a naive baseline.
   - Retrain with `python scripts/entrainer_modele.py`: it rewrites `models/modele_consommation.joblib` and `models/metriques.json`.

3. **Data Sources**:
   - French energy consumption data: **RTE eco2mix**.
   - Regional population statistics: **INSEE**.
   - Regional temperature data: **Météo France**.
   - European energy data: **Eurostat**.

---

## 🔧 Installation

To run the application locally, follow these steps. The dependencies are tested with **Python 3.12**, the version used on Streamlit Community Cloud.

### 1. Clone the Repository

```bash
git clone https://github.com/cnoret/hexa-watts.git
cd hexa-watts
```

### 2. Create a Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run streamlit_app.py
```

### 5. Run the Tests

```bash
pip install -r requirements-dev.txt
ruff check .
python -m pytest
```

The tests (about 20 seconds) check that the seven pages run without exceptions, that the prediction works and reacts to temperature, and that the pinned dependencies install without conflicts. GitHub Actions runs them, along with `ruff check`, on every push and pull request (`.github/workflows/tests.yml`). Dependabot proposes dependency updates once a month (`.github/dependabot.yml`).

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Sign in at [share.streamlit.io](https://share.streamlit.io) with the GitHub account that owns the repository.
2. Click **Create app**, then **Deploy a public app from GitHub**.
3. Repository `cnoret/hexa-watts`, branch `main`, main file path `streamlit_app.py`.
4. Open **Advanced settings** and select **Python 3.12**. This cannot be changed after deployment without deleting and redeploying the app.
5. Click **Deploy**. The first build takes a few minutes; the data files (about 93 MB) are part of the repository, so nothing else needs to be uploaded.

The app stays under about 700 MB of RAM: the large Parquet files are aggregated on load and only small summary tables are cached.

---

## 📂 Project Structure

```
hexa-watts/
├── datasets/                # Data files used for analysis and predictions
├── models/                  # Trained prediction model and its test metrics
├── content/                 # Modular Streamlit pages (e.g., Introduction, Visualizations)
├── images/                  # Image assets for the application
├── scripts/                 # Model training script
├── tests/                   # Automated tests (pytest and Streamlit AppTest)
├── streamlit_app.py         # Main application entry point
├── requirements.txt         # Dependencies for the project
├── requirements-dev.txt     # Dependencies plus test tools
└── README.md                # Project documentation
```

---

## 📊 Data Sources

1. [RTE Eco2Mix](https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def)
2. [INSEE Statistics](https://www.insee.fr/fr/statistiques)
3. [Météo France](https://donneespubliques.meteofrance.fr)
4. [Eurostat](https://ec.europa.eu/eurostat)

---

## 🧬 Technologies Used

- **Python**: Primary programming language.
- **Streamlit**: Framework for building the web application.
- **Pandas**: Data manipulation and analysis.
- **Plotly**: Interactive visualizations.
- **Scikit-Learn**: Machine learning for predictions.
- **Joblib**: Model serialization.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
