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
*   [x] **Lighweight Model Implementation**:
    *   Develop/Integrate a fast classifier (e.g., using domain blocklists, regex-based heuristics, or a lightweight Random Forest model).
    *   Implementing `OnlineClassifier` using XGBoost with ONNX runtime for fast inference.
    *   Added malicious pattern matching for known threat indicators.
*   [x] **API Integration**:
    *   Update the `/api/v1/url/shorten` endpoint to call the Tier 1 classifier.
    *   Reject URLs classified as `MALICIOUS` with a `422 Unprocessable Content`.
    *   Log classification results for further training.
    *   Integrated classifier service into URL shortening endpoint.
    *   Added proper error handling and response codes for malicious URLs.
    *   Classification results are now stored in the database with threat scores and timestamps.

## 🔍 Phase 3: Tier 2 - Offline (Deep) Classification
*   [x] **Heavyweight Model Implementation**:
    *   Implemented `BertUrlClassifier` using URL-BERT model with ONNX runtime.
    *   Classification results stored with threat scores and timestamps.
*   [x] **Background Worker Setup**:
    *   Implemented Celery worker with Redis broker for task processing.
    *   Celery beat schedules `classify_pending_batch` task hourly.
    *   Flower dashboard for task monitoring (port 5555).
    *   Docker Compose includes worker, beat, and flower services.
*   [x] **Automatic Remediation**:
    *   URLs classified as `MALICIOUS` are automatically disabled (`is_active=False`).
    *   [ ] Notify URL owners (if applicable) - future enhancement.

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
