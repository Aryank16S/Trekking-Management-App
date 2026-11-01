import numpy as np

DIFFICULTY_NUMERIC = {
    "Easy": 1.0,
    "Moderate": 2.0,
    "Hard": 3.0
}

class FitnessReadinessPredictor:
    """
    Machine Learning and Physiological Assessment Engine to evaluate
    a hiker's trail readiness, risk level, and customized training plan.
    Enhanced to directly ingest telemetry and biometrics from Smartwatches
    (Apple Watch, Garmin, Strava, Fitbit, Samsung Health, Web Bluetooth).
    """

    def predict(self, age, weekly_exercise, prior_treks, high_alt_exp,
                has_medical, difficulty, duration,
                resting_heart_rate=None, vo2_max=None, spo2_pct=None,
                elevation_gain_m=None, device_source=None):
        """
        Predicts readiness percentage, risk category, and personalized training regimen.
        Integrates wearable biometrics when available.
        """
        age = float(max(14, min(80, age)))
        exercise = float(max(0, min(30, weekly_exercise)))
        treks = float(max(0, min(50, prior_treks)))
        high_alt = 1.0 if high_alt_exp else 0.0
        medical = 1.0 if has_medical else 0.0
        diff = DIFFICULTY_NUMERIC.get(difficulty, 2.0)
        dur = float(max(1, min(30, duration)))

        # Physiological Fitness Capacity Score (0 to 100)
        fitness_capacity = 36.0
        fitness_capacity += min(32.0, exercise * 5.0)  # Weekly exercise
        fitness_capacity += min(16.0, treks * 3.5)     # Trail experience
        fitness_capacity += 10.0 * high_alt            # Altitude experience
        if medical == 1.0:
            fitness_capacity -= 20.0                   # Medical constraint

        # Biometric adjustments from Smartwatch Telemetry
        biometrics_applied = []
        if vo2_max is not None and float(vo2_max) > 0:
            v = float(vo2_max)
            if v >= 50.0:
                fitness_capacity += 12.0
                biometrics_applied.append(f"High VO2 Max ({v} ml/kg/min): Exceptional aerobic capacity for altitude")
            elif v >= 43.0:
                fitness_capacity += 6.0
                biometrics_applied.append(f"Good VO2 Max ({v} ml/kg/min): Solid cardiovascular endurance")
            elif v < 36.0:
                fitness_capacity -= 8.0
                biometrics_applied.append(f"Lower VO2 Max ({v} ml/kg/min): Aerobic conditioning recommended")

        if resting_heart_rate is not None and float(resting_heart_rate) > 0:
            rhr = float(resting_heart_rate)
            if rhr <= 55.0:
                fitness_capacity += 8.0
                biometrics_applied.append(f"Athletic Resting Heart Rate ({rhr} BPM): Efficient cardiac stroke volume")
            elif rhr <= 68.0:
                fitness_capacity += 3.0
                biometrics_applied.append(f"Healthy Resting Heart Rate ({rhr} BPM)")
            elif rhr >= 78.0:
                fitness_capacity -= 6.0
                biometrics_applied.append(f"Elevated Resting Heart Rate ({rhr} BPM): Recommend low-intensity base training")

        if elevation_gain_m is not None and float(elevation_gain_m) > 0:
            ele = float(elevation_gain_m)
            if ele >= 400.0:
                fitness_capacity += 8.0
                biometrics_applied.append(f"Proven Elevation Conditioning ({ele:.0f}m ascent logged on watch)")
            elif ele >= 150.0:
                fitness_capacity += 4.0
                biometrics_applied.append(f"Hill Climbing Training ({ele:.0f}m ascent logged)")

        if spo2_pct is not None and float(spo2_pct) > 0:
            spo2 = float(spo2_pct)
            if spo2 >= 97.0:
                fitness_capacity += 2.0
            elif spo2 < 95.0:
                fitness_capacity -= 6.0
                biometrics_applied.append(f"Baseline SpO2 at {spo2}%: Special attention to gradual acclimatization required")

        # Age stamina curve
        if age > 45:
            fitness_capacity -= (age - 45) * 0.75
        elif age < 18:
            fitness_capacity -= (18 - age) * 1.5

        fitness_capacity = max(10.0, min(100.0, fitness_capacity))

        # Trek Demand Score (0 to 100)
        trek_demand = (diff * 22.0) + (dur * 3.2)
        trek_demand = max(20.0, min(110.0, trek_demand))

        # Calibrated Sigmoid Activation on capacity vs demand
        delta = (fitness_capacity - trek_demand) / 18.0
        readiness_prob = 1.0 / (1.0 + np.exp(-delta))

        # Map to 0-100 percentage
        readiness_pct = int(round(readiness_prob * 100.0))
        readiness_pct = max(15, min(99, readiness_pct))

        # Risk Classification
        if readiness_pct >= 75:
            risk_level = "Low Risk"
            risk_badge = "success"
            verdict = "Excellent Physical Readiness"
            summary = "Your aerobic capacity, cardiac metrics, and conditioning align great with this trail. You are well prepared to summit."
        elif readiness_pct >= 55:
            risk_level = "Moderate Risk"
            risk_badge = "warning"
            verdict = "Moderately Prepared - Conditioning Recommended"
            summary = "You can successfully summit this trek with 2-3 weeks of targeted aerobic conditioning, incline walking, and stair intervals."
        else:
            risk_level = "High Risk"
            risk_badge = "danger"
            verdict = "Demanding Physical Challenge - Preparation Required"
            summary = "This trek's elevation and duration significantly exceed your current baseline. We strongly recommend 4-6 weeks of preparatory training or beginning with an easier trail."

        # Actionable AI Training Regimen
        tips = []
        if exercise < 3.5:
            tips.append("Gradually ramp up to 4+ hours of weekly cardio (jogging, cycling, or brisk incline walking).")
        if dur >= 4 and treks < 2:
            tips.append("Undertake 1-2 weekend practice day-hikes carrying a 6-8 kg loaded backpack to condition shoulder and back muscles.")
        if diff in [2.0, 3.0] and not high_alt_exp:
            tips.append("Practice rhythmic pursed-lip breathing and maintain high fluid intake (3.5 to 4 liters/day) to prevent altitude fatigue.")
        if resting_heart_rate and float(resting_heart_rate) > 72:
            tips.append("Integrate 2x weekly zone 2 steady-state endurance sessions (45 mins) to lower your resting heart rate and improve aerobic efficiency.")
        if has_medical:
            tips.append("Obtain medical clearance from your physician and ensure all emergency medications are stored in your immediate daypack.")
        if not tips:
            tips.append("Incorporate leg strengthening exercises (squats, lunges, calf raises) 3 days a week.")
            tips.append("Wear and break in your trekking boots 2 weeks before departure to prevent trail blisters.")

        return {
            "readiness_pct": readiness_pct,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "verdict": verdict,
            "summary": summary,
            "tips": tips,
            "biometrics_applied": biometrics_applied,
            "device_source": device_source
        }


# Singleton instance
fitness_predictor = FitnessReadinessPredictor()
