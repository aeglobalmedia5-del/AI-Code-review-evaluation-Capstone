Overview
========

AI Code Review Evaluation Dashboard
Capstone project demonstrating AI-powered code review, quality evaluation, governance validation, deployment readiness assessment, and LLM output monitoring using Gemini, DeepEval, RAGAS, and Streamlit.

Features
========

✅ DeepEval Evaluation
✅ RAGAS Validation
✅ Quality Gate Verification
✅ Security & Compliance Checks
✅ Drift Monitoring
✅ Deployment Readiness Assessment
✅ Automated Report Generation
✅ Interactive Streamlit Dashboard
✅ GO / NO-GO Production Recommendation


Solution Architecture
=====================

Dataset
   │
   ▼
Gemini / Groq
   │
   ▼
Evaluation Engine
   │
┌──┼──────────┬──────────┬──────────┐
▼  ▼          ▼          ▼          ▼

DeepEval   Security   Governance   Drift

               │
               ▼

       Report Generation

               │
               ▼

      Streamlit Dashboard

               │
               ▼

      GO / NO-GO Decision

Technology Stack
================

Python
Streamlit
DeepEval
RAGAS
Gemini
Groq
Pandas
JSON Reporting

Project Structure
===================

ai_code_review_evaluation/
│
├── reports/
│   ├── final_summary.json
│   ├── quality_gate.json
│   ├── drift_incident.json
│   ├── compliance_checklist.json
│   └── ...
│
├── src/
│   └── ai_review_eval/
│       ├── evaluation.py
│       ├── quality_gate.py
│       ├── governance.py
│       ├── security.py
│       ├── drift.py
│       └── main.py
│
├── tests/
│
├── data/
│
├── streamlit_app.py
│
├── requirements.txt
│
└── README.md

How to Run
-----------
Install Dependencies
pip install -r requirements.txt

Run Evaluation Pipeline
python -m ai_review_eval.main

Launch Dashboard
streamlit run streamlit_app.py

Dashboard Modules
================
📊 Dashboard
Evaluation Metrics
Production Readiness
Executive Summary
KPI Cards

✅ Quality Gate
Evaluation Status
Security Validation
Compliance Validation
Deployment Readiness

📄 Reports
Generated Reports
Downloadable Artifacts

🏗️ Architecture
System Design
Component Overview

📘 Project Info
Technology Stack
Features Overview

Results

✅ Quality Gates Passed

✅ Security Validation Passed

✅ Compliance Validation Passed

✅ Drift Monitoring Active

✅ Deployment Readiness Verified

✅ Governance Controls Enabled

🟢 Final Recommendation

GO TO PRODUCTION

All evaluation, governance, security, compliance, monitoring, and deployment readiness checks have been successfully completed.

Screenshots
<img width="959" height="266" alt="image" src="https://github.com/user-attachments/assets/12c3b1f1-8eea-46b0-8766-7d9341d39091" />
<img width="952" height="372" alt="Quality Gate results" src="https://github.com/user-attachments/assets/ab971041-0f6f-4bb7-a212-9cd4eb05a4a2" />
<img width="941" height="341" alt="Evaluation Metrics Dashboard" src="https://github.com/user-attachments/assets/b14f97f0-82eb-4d49-a22d-c0ce7164b4ac" />



Author

Dhaanvaanth S
 AI Evaluation & Governance Capstone Project
