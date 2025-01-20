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
   - Linear Regression model trained on historical data.

3. **Data Sources**:
   - French energy consumption data: **RTE eco2mix**.
   - Regional population statistics: **INSEE**.
   - Regional temperature data: **Météo France**.
   - European energy data: **Eurostat**.

---

## 🔧 Installation

To run the application locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/energie-france.git
cd energie-france
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
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

---

## 📂 Project Structure

```
energie-france/
├── datasets/                # Data files used for analysis and predictions
├── models/                  # Pre-trained ML models (e.g., Linear Regression)
├── content/                 # Modular Streamlit pages (e.g., Introduction, Visualizations)
├── images/                  # Image assets for the application
├── streamlit_app.py         # Main application entry point
├── requirements.txt         # Dependencies for the project
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
