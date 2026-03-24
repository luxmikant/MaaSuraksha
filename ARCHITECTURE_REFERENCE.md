# MaaSuraksha: Quick Reference Guide
## System Architecture & Data Preprocessing

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  (Mothers & ASHA Workers)                                        │
├─────────────────────────────────────────────────────────────────┤
│         🌐 Web Interface (HTML/CSS/JavaScript)                   │
│    ┌──────────────┐  ┌─────────────┐  ┌──────────────┐           │
│    │  Login Page  │  │  Form Page  │  │  Dashboard   │           │
│    └──────────────┘  └─────────────┘  └──────────────┘           │
│                    Multi-language i18n                            │
│                   Theme Switching Support                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/POST/GET
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER (Flask)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐   ┌─────────────────┐  ┌──────────────┐   │
│  │  Auth Routes    │   │ Predict Routes  │  │  Data Routes │   │
│  ├─────────────────┤   ├─────────────────┤  ├──────────────┤   │
│  │ /auth/signup    │   │ /api/predict    │  │ /api/alerts  │   │
│  │ /auth/login     │   │ (Main ML Engine)│  │ /api/tracker │   │
│  │ /auth/logout    │   │                 │  │              │   │
│  └─────────────────┘   └─────────────────┘  └──────────────┘   │
│         │                      │                    │             │
│         └──────────┬───────────┴────────────────────┘             │
│                    ▼                                               │
│            ┌─────────────────────┐                               │
│            │  Data Validation    │                               │
│            │  Feature Extraction │                               │
│            │  Session Management │                               │
│            └─────────────────────┘                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ML & DATABASE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐      ┌──────────────────────────────┐ │
│  │  ML Model Component  │      │   SQLite Database            │ │
│  ├──────────────────────┤      ├──────────────────────────────┤ │
│  │  maternal_risk_      │      │  Table: predictions          │ │
│  │  model.pkl           │      │    ├─ id                     │ │
│  │  (Serialized)        │      │    ├─ age                    │ │
│  │                      │      │    ├─ blood_pressure         │ │
│  │  Features In:        │      │    ├─ hemoglobin            │ │
│  │  • Age               │      │    ├─ complications          │ │
│  │  • DiastolicBP       │      │    ├─ risk_level             │ │
│  │  • BS                │      │    └─ timestamp              │ │
│  │  • BodyTemp          │      │                              │ │
│  │  • HeartRate         │      │  Table: daily_tracker        │ │
│  │                      │      │    ├─ mood                   │ │
│  │  Output (3 classes): │      │    ├─ water_intake           │ │
│  │  • 0 = Low Risk      │      │    ├─ sleep_hours            │ │
│  │  • 1 = Mid Risk      │      │    ├─ symptoms               │ │
│  │  • 2 = High Risk     │      │    └─ timestamp              │ │
│  │                      │      │                              │ │
│  └──────────────────────┘      │  Table: users                │ │
│                                │    ├─ username               │ │
│                                │    ├─ password               │ │
│                                │    └─ role                   │ │
│                                │                              │ │
│  Algorithms Tested:            └──────────────────────────────┘ │
│  1. Logistic Regression                                          │
│  2. K-Nearest Neighbors (KNN)                                    │
│  3. Random Forest (Best Performer)  ⭐                           │
│  4. Gradient Boosting Classifier                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 DATA PREPROCESSING PIPELINE

```
STAGE 1: DATA INGESTION
┌─────────────────────────────────────────┐
│  Source: IoT-based Health Monitoring    │
│  Dataset: 1,014 maternal health records │
│  Origin: Hospitals, clinics, communities│
│  Format: CSV (Kaggle dataset)           │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 2: EXPLORATORY DATA ANALYSIS (EDA)
┌─────────────────────────────────────────┐
│  ✓ Check for missing values (NONE!)     │
│  ✓ Data types verification              │
│  ✓ Statistical summary (mean, std, etc) │
│  ✓ Distribution analysis per risk level │
│  ✓ Identify outliers (histograms)       │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 3: DATA TRANSFORMATION
┌─────────────────────────────────────────┐
│  Convert Temperature:                   │
│  Fahrenheit → Celsius                   │
│  Formula: (°F - 32) × 5/9               │
│  Example: 98.6°F → 37°C                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 4: FEATURE ANALYSIS & SELECTION
┌─────────────────────────────────────────┐
│  Initial Features (7):                  │
│  • Age                                  │
│  • SystolicBP                           │
│  • DiastolicBP      ⭐ SELECTED         │
│  • BS (Blood Sugar)                     │
│  • BodyTemp                             │
│  • HeartRate                            │
│  • RiskLevel (TARGET)                   │
│                                         │
│  Multicollinearity Check (VIF):         │
│  • Remove: SystolicBP (correlated)      │
│  • Keep: All 5 features + target        │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 5: FEATURE SCALING
┌─────────────────────────────────────────┐
│  StandardScaler Normalization:          │
│  ───────────────────────────────         │
│  After scaling:                         │
│  • Mean = 0                             │
│  • Std Dev = 1                          │
│  • Comparable scales for all features   │
│                                         │
│  Why? KNN, Logistic Regression          │
│  sensitive to magnitude differences     │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 6: DATA SPLITTING
┌─────────────────────────────────────────┐
│  Total: 1,014 records                   │
│                                         │
│  Training Set: 80% = 811 records ──┐   │
│  Test Set: 20% = 203 records       ├─→ │
│                                    │   │
│  Random State: 42 (reproducible)  └─→ │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 7: MODEL TRAINING & VALIDATION
┌─────────────────────────────────────────┐
│  Train 4 Classifiers:                   │
│  1. Logistic Regression                 │
│     └─ Accuracy: ~70-75%                │
│  2. KNN (k=5)                           │
│     └─ Accuracy: ~75-80%                │
│  3. Random Forest (100 trees)  ⭐       │
│     └─ Accuracy: ~80-85%                │
│  4. Gradient Boosting                   │
│     └─ Accuracy: ~80-82%                │
│                                         │
│  Hyperparameter Tuning via              │
│  Grid Search + 5-Fold Cross Validation  │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 8: MODEL EVALUATION
┌─────────────────────────────────────────┐
│  Metrics Calculated:                    │
│  • Accuracy (overall correctness)       │
│  • Precision (true positives ratio)     │
│  • Recall (sensitivity)                 │
│  • F1-Score (harmonic mean)             │
│  • Confusion Matrix                     │
│  • Classification Report (per class)    │
│                                         │
│  Focus: High Recall for High-Risk Class │
│  (minimize false negatives)             │
└────────────────┬────────────────────────┘
                 │
                 ▼
STAGE 9: MODEL SERIALIZATION & DEPLOYMENT
┌─────────────────────────────────────────┐
│  Save Best Model:                       │
│  joblib.dump(model, 'maternal_risk...') │
│  File: maternal_risk_model.pkl          │
│                                         │
│  Load on App Startup:                   │
│  model = joblib.load(MODEL_PATH)        │
│  Ready for inference!                   │
└─────────────────────────────────────────┘
```

---

## 🎯 REAL-TIME PREDICTION FLOW

```
USER SUBMITS FORM (form.html)
    ↓
┌─────────────────────────────────────────────────────┐
│   Input Collection                                  │
│   ─────────────────────────────────────            │
│   • Mother's Age: 28 years                         │
│   • Gestational Month: 6                           │
│   • Blood Pressure: 120/80 mmHg                    │
│   • Hemoglobin: 12.5 g/dL                          │
│   • Previous Complications: No                     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   JavaScript Validation                             │
│   (Detect missing/invalid fields)                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Send AJAX Request to Backend                     │
│   POST /api/predict                                │
│   Content-Type: application/json                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Flask Backend (/api/predict)                     │
│   ─────────────────────────────────────            │
│   1. Parse JSON request                            │
│   2. Extract form fields                           │
│   3. Validate data types                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Feature Extraction & Mapping                     │
│   ─────────────────────────────────────            │
│   Form Input → ML Features                         │
│   ├─ age: 28          → Feature[0]: 28            │
│   ├─ bp: "120/80"     → Feature[1]: 80 (diastolic)│
│   ├─ Previous BS data → Feature[2]: 7.0           │
│   ├─ Body temp       → Feature[3]: 37.0           │
│   └─ Heart rate      → Feature[4]: 75             │
│                                                    │
│   Feature Vector: [28, 80, 7.0, 37.0, 75]        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Load & Apply ML Model                            │
│   ─────────────────────────────────────            │
│   Model: maternal_risk_model.pkl                   │
│   Input: [28, 80, 7.0, 37.0, 75] (scaled)        │
│   Prediction: 0 (integer label)                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Map Class Labels to Risk Levels                  │
│   ─────────────────────────────────────            │
│   0 → "Low Risk"    🟢 (Green)                      │
│   1 → "Mid Risk"    🟡 (Orange)                     │
│   2 → "High Risk"   🔴 (Red)                        │
│                                                    │
│   Result: "Low Risk"                               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Save to Database (SQLite)                        │
│   ─────────────────────────────────────            │
│   INSERT INTO predictions                          │
│   (age, gestational_month, blood_pressure,         │
│    hemoglobin, complications, risk_level,          │
│    timestamp)                                      │
│   VALUES (28, 6, '120/80', 12.5, 'No',             │
│           'Low Risk', CURRENT_TIMESTAMP)           │
│                                                    │
│   ✓ Record saved with ID (auto-increment)         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Send JSON Response to Frontend                   │
│   ─────────────────────────────────────            │
│   {                                                 │
│     "status": "success",                           │
│     "risk_level": "Low Risk"                       │
│   }                                                 │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│   Display Result to User                           │
│   ─────────────────────────────────────            │
│   Risk Level: Low Risk ✅                           │
│   Recommendation: Continue routine monitoring      │
│   Next Follow-up: As per schedule                  │
│   Share Results: Optional save/print               │
└─────────────────────────────────────────────────────┘
```

---

## 📈 DATASET STATISTICS

### **Class Distribution**
| Risk Level | Count | Percentage | Color |
|-----------|-------|-----------|----------|
| Low Risk  | 406   | 40%       | 🟢 Green |
| Mid Risk  | 336   | 33%       | 🟡 Orange|
| High Risk | 272   | 27%       | 🔴 Red   |
| **Total** | **1,014** | **100%** | - |

### **Feature Statistics**

| Feature | Mean | Std Dev | Min | Max | Unit |
|---------|------|---------|-----|-----|------|
| Age | ~29.9 | ~13.2 | 10 | 70 | years |
| DiastolicBP | ~72.9 | ~7.6 | 50 | 100 | mmHg |
| BS (Blood Sugar) | ~8.5 | ~3.0 | 6.0 | 19.0 | mmol/L |
| BodyTemp | ~36.5 | ~1.5 | 35.0 | 38.0 | °C |
| HeartRate | ~75.3 | ~8.2 | 60 | 100 | bpm |

---

## 🔑 KEY FEATURES EXPLAINED

### **1. Age**
- **Why it matters**: Advanced maternal age (>35) increases risks
- **Data collected**: Self-reported or from medical records
- **Impact on model**: Significant weight for high-risk prediction

### **2. Diastolic Blood Pressure** ⭐ (PRIMARY INDICATOR)
- **Why it matters**: Detects pre-eclampsia and hypertension in pregnancy
- **Normal range**: <80 mmHg
- **Risk threshold**: >90 mmHg indicates elevated risk
- **Data source**: Manual BP cuff or automatic monitor

### **3. Blood Sugar (BS)**
- **Why it matters**: Screen for gestational diabetes
- **Normal fasting**: 3.9-5.8 mmol/L
- **Diagnosis range**: >7 mmol/L after fasting
- **Data source**: Blood tests or continuous glucose monitors

### **4. Body Temperature**
- **Why it matters**: Fever may indicate infection/complications
- **Normal range**: 36.1-37.2°C
- **Elevated**: >37.5°C requires investigation
- **Data collected**: Digital thermometer

### **5. Heart Rate**
- **Why it matters**: Tachycardia may indicate stress/complications
- **Normal pregnancy range**: 70-90 bpm (increases through pregnancy)
- **Data collected**: Pulse measurement or wearable devices

---

## 🏥 RISK CLASSIFICATION LOGIC

```
Input: [Age, DiastolicBP, BS, BodyTemp, HeartRate]
            │
            ▼
      ML Model Decision
            │
    ───────┴────────────
    │      │            │
    ▼      ▼            ▼
Low Risk Mid Risk  High Risk
 (0)      (1)        (2)

SCORING CONCEPTUALLY:
─────────────────────────────

LOW RISK (Green) ✅
├─ Age: <30 years
├─ DiastolicBP: <80 mmHg
├─ BS: 6.0-8.0 mmol/L
├─ BodyTemp: 36.5-37.0°C
└─ HeartRate: 70-80 bpm

MID RISK (Orange) ⚠️
├─ Age: 30-35 years
├─ DiastolicBP: 80-90 mmHg
├─ BS: 8.0-10.0 mmol/L
├─ BodyTemp: 37.0-37.5°C
└─ HeartRate: 80-90 bpm

HIGH RISK (Red) 🔴
├─ Age: >35 years
├─ DiastolicBP: >90 mmHg
├─ BS: >10.0 mmol/L
├─ BodyTemp: >37.5°C
└─ HeartRate: >90 bpm
```

---

## 🔧 TECH STACK SUMMARY

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) | User interface |
| **i18n** | translations.js | Multi-language support |
| **Backend** | Flask (Python) | API server |
| **Database** | SQLite | Data persistence |
| **ML** | scikit-learn | Model training & inference |
| **Model Serialization** | joblib | Model persistence |
| **Data Processing** | pandas, numpy | Data manipulation |
| **Visualization** | matplotlib, seaborn | EDA charts |
| **Deployment Ready** | Gunicorn, Nginx | Production scale |

---

## ✅ DATA QUALITY ASSURANCE

### **Checks Performed**
- [x] No missing values in dataset
- [x] Proper data types (int, float)
- [x] Outlier detection and analysis
- [x] Multicollinearity testing (VIF)
- [x] Class balance assessment
- [x] Feature scaling validation
- [x] Train-test split randomization
- [x] Cross-validation (5-fold)

### **Potential Issues & Mitigation**
| Issue | Mitigation |
|-------|-----------|
| Imbalanced classes (27% High Risk) | Use weighted loss, adjust threshold |
| Outliers in features | Robust scaling, outlier detection |
| Missing IoT data fields | Use derived features or defaults |
| Model drift over time | Periodic retraining with new data |

---

## 📱 USER WORKFLOWS

### **For Mothers (Patients)**
1. Sign up with username/password
2. Fill screening form
3. Get instant risk assessment
4. Log daily health tracker
5. View historical trends on dashboard
6. Optional: Share results with ASHA/Doctor

### **For ASHA Workers (Health Volunteers)**
1. Login with ASHA credentials
2. Enter pregnant woman's data
3. Generate risk report
4. Track multiple patients
5. Identify high-risk cases for home visits
6. Monitor community health metrics

### **For Healthcare Administrators (Future)**
1. View aggregate statistics
2. Export reports for analysis
3. Manage user accounts & roles
4. Monitor system performance
5. Update clinical guidelines

---

## 🚀 DEPLOYMENT READINESS CHECKLIST

- [x] Model training completed & saved
- [x] Backend API implemented
- [x] Frontend interface functional
- [x] Database schema created
- [x] Authentication system
- [ ] SSL/HTTPS configuration
- [ ] API documentation (Swagger)
- [ ] Unit & integration tests
- [ ] Load testing
- [ ] Security audit
- [ ] Compliance review (HIPAA/GDPR)
- [ ] Monitoring & logging setup

---

## 📞 CONTACT & SUPPORT

For questions about system architecture or data preprocessing:
- Technical Documentation: See PRESENTATION_SCRIPT.md
- Code Repository: MaaSuraksha project
- Dataset: Kaggle - Maternal Health Risk Data Set

---

**Document Version**: 1.0  
**Last Updated**: March 2026  
**Status**: Ready for Presentation
