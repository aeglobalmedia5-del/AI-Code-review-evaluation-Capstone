Overview
========

The AI Code Review Evaluation Dashboard is an end-to-end AI Evaluation & Governance platform developed as a capstone project. The solution evaluates Large Language Model (LLM) outputs using automated quality metrics, governance controls, security validation, deployment readiness checks, and production quality gates.

The project provides a Streamlit-based dashboard that visualizes evaluation results, generated reports, architecture, and production recommendations.

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

Author

Dhaanvaanth S
 AI Evaluation & Governance Capstone Project