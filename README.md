# 3D Print Failure Predictor

I built this after getting frustrated with failed prints on my Bambu Lab A1 Mini. 
There's no public dataset for slicer-parameter-based failure prediction, so I built one 
from scratch using Bambu's official documentation and real FDM failure patterns.

## What it does

Takes your slicer settings as input and tells you:
- Whether your print is likely to fail
- The probability of failure
- Exactly what to change to fix it

## How I built it

**Dataset** — Simulated 300 print jobs with failure rules based on actual Bambu A1 Mini 
constraints. Rules like "TPU above 50mm/s jams", "vertical prints without supports fail 
79% of the time" — not random noise, actual physics.

**EDA** — Explored failure patterns across orientation, supports, speed, and complexity. 
Biggest finding: vertical + no supports is by far the deadliest combination at 79% failure rate.

**Modeling** — Trained Logistic Regression and Random Forest. RF won on accuracy (78%) 
but LR was actually better at catching real failures. Learned that accuracy alone is misleading.

**Recommender** — Rule-based system on top of the model. Doesn't just say "this will fail" 
— tells you to reduce speed, add supports, or change orientation based on what's actually wrong.

**Streamlit app** — Simple UI where you dial in your settings and get an instant prediction 
with recommendations.

## Results

| Model | Accuracy |
|-------|----------|
| Random Forest | 78% |
| Logistic Regression | 77% |

Top failure predictors: orientation, supports, print speed

## Stack

Python · Pandas · Scikit-learn · Seaborn · Streamlit

## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```
├── analysis.ipynb       # full EDA and modeling walkthrough
├── generate_data.py     # how the dataset was built
├── app.py               # streamlit app
├── print_jobs.csv       # the dataset
└── rf_model.pkl         # saved model
```

## Honest disclaimer

The dataset is synthetic — built from documented Bambu A1 Mini constraints, not real 
print logs. The goal was to validate that a model can learn known FDM failure relationships 
and provide a framework that could be extended with real print data.
