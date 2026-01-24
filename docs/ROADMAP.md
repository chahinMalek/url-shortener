# Roadmap: ML-Powered URL Classification

This document outlines the plan for integrating machine learning into the URL shortener to identify and block malicious URLs using a 2-tier classification approach.

## 🎯 Goal
To enhance safety by preventing the shortening of malicious URLs and providing continuous monitoring of the URLs stored in our database.

---

## 🏗️ Phase 1: Foundation & Infrastructure
*   [x] **Schema Update**:
    *   Add classification fields to `Url` entity and `UrlModel`:
        *   `safety_status`: Enum (PENDING, SAFE, MALICIOUS, SUSPICIOUS)
        *   `threat_score`: Float (0.0 to 1.0)
        *   `classified_at`: DateTime
        *   `classifier`: String (to track which model performed the scan)
*   [x] **ML Service Layer**:
    *   Define a standard interface `BaseUrlClassifier` for all classification models.
    *   Define regex-based classifier as a placeholder or ensemble classifier.

## ⚡ Phase 2: Tier 1 - Online (Fast) Classification
*   [ ] **Lighweight Model Implementation**:
    *   Develop/Integrate a fast classifier (e.g., using domain blocklists, regex-based heuristics, or a lightweight Random Forest model).
    *   Target latency: < 50ms.
*   [ ] **API Integration**:
    *   Update the `/api/v1/url/shorten` endpoint to call the Tier 1 classifier.
    *   Reject URLs classified as `MALICIOUS` with a `422 Unprocessable Content`.
    *   Log classification results for further training.

## 🔍 Phase 3: Tier 2 - Offline (Deep) Classification
*   [ ] **Heavyweight Model Implementation**:
    *   Implement a robust classifier using deep learning (e.g., URL-based BERT or LSTM) or a feature-heavy ensemble model.
    *   Integrate third-party security APIs (e.g., Google Safe Browsing, VirusTotal) as additional features.
*   [ ] **Background Worker Setup**:
    *   Implement a background job (using Celery, APScheduler, or a standalone worker) to scan `PENDING` or newly added URLs.
    *   Set up periodic re-scans for existing `SAFE` URLs to detect late-onset threats.
*   [ ] **Automatic Remediation**:
    *   Implement logic to set `is_active=False` for URLs identified as malicious by the Tier 2 model.
    *   Notify URL owners (if applicable).

## 📊 Phase 4: Monitoring & Refinement
*   [ ] **Dashboards**:
    *   Visualize classification stats (safe vs. malicious ratios, model confidence).
    *   Monitor false positive/negative rates.
*   [ ] **Feedback Loop**:
    *   Create an admin endpoint to manually override classifications.
    *   Use corrected data to periodically retrain models.
*   [ ] **Testing & Validation**:
    *   Create a benchmark dataset of malicious and safe URLs.
    *   Automate performance testing for ML models.
