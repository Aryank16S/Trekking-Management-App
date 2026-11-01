# TrekMate - AI-Powered Trekking Management System

## Overview

**TrekMate** is an intelligent, web-based Trekking Management & Expedition Intelligence Platform developed with Python, Flask, and custom Machine Learning models. It provides role-based dashboards for **Administrators**, **Staff Members**, and **Users**, enhanced with cutting-edge **AI/ML capabilities**:

- ⌚ **Direct Smartwatch Fitness & Health Sync**: Transfer biometric data directly from Garmin, Apple Watch, Strava, Fitbit, Samsung Health, or in-browser Web Bluetooth to fuel personalized trail preparation.
- 🎯 **AI Trek Matchmaker**: Content-Based Filtering using TF-IDF and Cosine Similarity to recommend treks based on individual fitness, budget, duration, and terrain preference.
- 🫀 **ML Fitness Readiness & Risk Evaluator**: Machine Learning model evaluating participant summit readiness, altitude sickness (AMS) risk, and generating customized pre-trek conditioning plans.
- 🤖 **TrekBot AI Expedition Advisor**: 24/7 intelligent expedition guide providing real-time advice, automatic day-by-day itineraries, and customized packing checklists.
- 📈 **ML Demand Forecasting & Price Optimization**: Predictive analytics for Administrators tracking capacity utilization, demand tiers, and dynamic pricing strategies.

---

## Key Features

### ⌚ Smartwatch Fitness Sync Hub (`/ai/watch-sync`)
- **Direct File Dropzone**: Drag & drop any `.gpx`, `.tcx`, `.csv`, or `.json` activity file exported from Garmin Connect, Strava, Apple Health, or Samsung Health.
- **Direct Web Bluetooth API**: Live wireless pairing directly in your browser with any Bluetooth SIG Heart Rate & fitness band (Garmin, Polar H10, etc.) without requiring cables or third-party apps.
- **1-Click Cloud Sync Presets**: Instant one-click synchronization for Apple Watch, Garmin, Strava, Fitbit, and Samsung Health.
- **Biometric Extraction**: Automatically computes resting heart rate, VO2 max estimate, weekly active cardio hours, elevation climbed (meters), daily steps, and calories.
- **Direct ML Integration**: Ingested smartwatch metrics directly auto-fill and power the **ML Fitness Readiness & Altitude Risk Predictor**!

### 🧠 AI & Machine Learning Features
- **Smart Trek Matchmaker** (`/ai/matchmaker`): Hybrid TF-IDF vectorization across trail difficulty, elevation, and terrain combined with numerical constraint optimization.
- **Fitness Readiness Evaluator** (`/ai/readiness`): Evaluates age, weekly cardio hours, prior treks, high-altitude experience, and medical conditions against trail demands, enriched with smartwatch biometrics.
- **TrekBot AI Assistant** (`/ai/assistant`): Interactive chat with automated packing checklist generator (`/api/ai/packing/<id>`) and day-by-day expedition itinerary planner (`/api/ai/itinerary/<id>`).
- **Admin AI Analytics** (`/admin/ai-analytics`): Occupancy forecasting, demand tiering (High/Healthy/Moderate/Low), and dynamic pricing advice.

### 🛡️ Authentication & Security Controls
- Role-based access control: **Admin**, **Staff**, and **User**.
- Secure password hashing using Werkzeug `scrypt`.
- **24-Hour Login Rate Limiting**: Users and staff are limited to a maximum of **3 logins or attempts within 24 hours** to prevent brute-force and account misuse.
- **Admin Login Access Control**: Administrators can monitor 24-hour login counts, instantly unlock/reset login limits for any user or staff member with 1-click, or manually lock access directly from the Admin User & Staff Management dashboards.
- Staff account approval workflows and user blacklisting.

### 👥 User Capabilities
- Browse and search featured and all available treks.
- **Interactive Photo Slides Carousel**: Every available trek card features high-definition trail photo slides with auto-play, indicator dots, and previous/next slide navigation.
- One-click trek booking with real-time slot capacity tracking and duplicate booking prevention.
- Personal dashboard with personalized AI recommendations and booking management.

---

## Installation & Setup

### 1. Activate Virtual Environment
Windows:
```powershell
.\venv\Scripts\activate
```

### 2. Seed Database
```powershell
python Trekking-Management-App/seed.py
```

### 3. Run the Application
```powershell
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

#### Default Demo Credentials:
- **Admin**: `admin@gmail.com` / `admin123`
- **Staff**: `tenzing@trekmate.com` / `staff123`
- **User**: `user@gmail.com` / `user123`

---

## Automated Test Suite

Run the full automated test suite covering 29 test cases:
```powershell
python test_app.py
```
