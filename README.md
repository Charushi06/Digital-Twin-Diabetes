# Glucose Twin: Type 2 Diabetes Digital Twin (CGM + Wearable + Clinical Profile)

Research Prototype • Version 1.0.0 • October 2026

---

## 1. Executive Summary

**Glucose Twin** is a proof-of-concept digital twin for adults with type 2 diabetes or prediabetes who wear a continuous glucose monitor (CGM) and a consumer smartwatch. For each patient, the system maintains a persistent virtual model that updates as glucose, heart rate, metabolic activity, and logged meals arrive. It forecasts hyperglycaemic excursions up to 2 hours ahead, explains prediction drivers in plain clinical language, and provides a pre-meal what-if sensitivity tool for clinicians and dietitians.

### Stream Fusion Architecture
- **Static / Historical Clinical Profile:** Age, sex, BMI, HbA1c, fasting glucose, fasting insulin, HOMA-IR, lipid profile (triglycerides, HDL, LDL).
- **Dynamic Real-Time Streams:** Dexcom G6 Pro CGM (5-minute resampled grid), smartwatch heart rate and METs/activity calories, and macronutrient-logged meals (carbohydrates, protein, fat, dietary fiber).
- **Digital Twin Personalisation Step:** 48-hour warm-up calibration deriving personal mean glucose, glucose standard deviation, typical post-meal rise, and resting heart rate.

---

## 2. Problem Statement & Healthcare Use Case

- **Epidemiology in India:** An estimated 101 million people live with diabetes (11.4%) and 136 million with prediabetes (15.3%), per the ICMR-INDIAB national study (*Lancet Diabetes & Endocrinology* 2023; 11: 474-89).
- **Clinical Need:** Postprandial glucose spikes drive long-term microvascular and macrovascular complications. CGM data is traditionally reviewed retrospectively during infrequent clinic visits.
- **Twin Opportunity:** By fusing who a patient is (baseline clinical phenotype) with what they are experiencing right now (continuous physiological trajectory and upcoming meals), the twin provides early, explainable risk warnings and interactive what-if meal sensitivity analysis before meals occur.

---

## 3. Honesty Statement & Limitations

1. **Cohort Demographics:** The dataset contains **45 adults** recruited by Sansum Diabetes Research Institute in Santa Barbara, California, USA. It contains **no Indian participants**. The results demonstrate that the multimodal causal pipeline operates effectively on real biosignals and meals; they do **not** claim clinical validation on Indian populations.
2. **Indian Meal Presets:** The presets provided in the what-if sensitivity simulator are an **extrapolation** sourced from the Indian Food Composition Tables (NIN-ICMR, IFCT 2017) for illustrative clinician review.
3. **Sensor Scope:** The dataset contains heart rate and metabolic equivalent (METs) activity; it does not contain sleep stages or step count.
4. **Physiological Label:** The target event is a consensus hyperglycaemic excursion cut-off ($T = 180\text{ mg/dL}$ for $\ge 15\text{ minutes}$), not a downstream clinical outcome (e.g., HbA1c reduction or complication rate).

---

## 4. Key Empirical Findings: The Proof of Fusion

Evaluated across **45 held-out participants** using **5-fold Stratified Group Cross-Validation $\times$ 3 Seeds** with **1,000 participant-level bootstrap 95% Confidence Intervals** (Rule 2 & 5: zero data leakage, no participant in both train and test):

### Primary 120-Minute Horizon Model Comparison
| Model | AUROC | PR-AUC | Brier | ECE | Median Lead Time | Event Sensitivity (@ 2 alerts/day) |
|---|---|---|---|---|---|---|
| **B0a (Trend Arrow Rule)** | 0.624 [0.611, 0.639] | 0.234 [0.194, 0.284] | n/a | n/a | 40 min | 96.6% (excessive false alarms: 6.99/day) |
| **B0b (Simple Meal Rule)** | 0.511 [0.509, 0.513] | 0.148 [0.121, 0.187] | n/a | n/a | n/a | 0.0% |
| **B1 (Logistic Regression)** | 0.745 [0.690, 0.816] | 0.393 [0.322, 0.464] | 0.104 | 0.030 | 65 min | 49.7% |
| **B2 (LightGBM Monotone)** | **0.839 [0.802, 0.867]** | **0.507 [0.422, 0.565]** | **0.092** | **0.013** | **45 min** | **55.9% (1.69 alerts/day)** |

### Stream Fusion Ablation Proof (120-Minute Horizon)
| Variant | Inputs | PR-AUC | AUROC | Finding |
|---|---|---|---|---|
| **A0** | Glucose trajectory only | 0.426 [0.365, 0.480] | 0.784 [0.754, 0.810] | Baseline CGM trend alone |
| **A1** | A0 + Meal logs | 0.453 [0.393, 0.504] | 0.818 [0.794, 0.837] | Meal macros provide +0.027 PR-AUC lift |
| **A2** | A1 + Smartwatch (HR + METs) | 0.429 [0.375, 0.484] | 0.811 [0.784, 0.829] | Observational wearable noise slight dip |
| **A3** | A2 + Static clinical profile | 0.468 [0.390, 0.535] | 0.823 [0.791, 0.848] | HbA1c/BMI/HOMA-IR phenotypic anchor |
| **A4** | **Full Twin (A3 + Personal Baseline)** | **0.502 [0.432, 0.557]** | **0.835 [0.803, 0.863]** | **Highest performance across all metrics** |
| *Static Only* | Profile only (no dynamic CGM) | 0.273 [0.215, 0.324] | 0.724 [0.658, 0.771] | Proves static data alone cannot time excursions |

---

## 5. Technology Stack

- **Backend:** Python 3.11, FastAPI, LightGBM, Scikit-Learn, SHAP, PyArrow, Pydantic, Uvicorn.
- **Frontend:** React 19, Vite, Lucide Icons, Modern Vanilla CSS Design System (Dark mode, glassmorphism, responsive micro-animations).
- **Data Engine:** 5-minute causal grid resampling, participant-level cross-validation, causal feature builder.

---

## 6. How to Run Locally

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm

### 1. Setup Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.lock (or pandas numpy pyarrow scikit-learn lightgbm shap fastapi uvicorn)
```

### 2. Download Real Data & Build Features
```bash
python scripts/download_cgmacros.py
python scripts/audit.py
python scripts/build_dataset.py
python scripts/train.py
```

### 3. Launch Full-Stack Application
In terminal 1 (FastAPI Backend):
```bash
python -m uvicorn app.server:app --port 8000 --host 127.0.0.1
```

In terminal 2 (React Frontend):
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 7. Data License & Regulatory Disclaimers

- **Primary Dataset:** CGMacros v1.0.0 (PhysioNet, DOI: 10.13026/3z8q-x658).
- **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (**CC BY-NC-SA 4.0**).
- **Regulatory Status:** This software is a research prototype developed for academic demonstration and evaluation. It is **not** a cleared medical device, does not diagnose disease, and does not prescribe therapy.
- **Mandatory Disclaimers:**
  - *"Advisory forecast from a research prototype. Not a diagnosis."*
  - *"Sensitivity analysis on model inputs. Not a treatment simulation, not proof of causation, not medical advice."*
  - *"Replay of recorded data. Not a live patient."*
