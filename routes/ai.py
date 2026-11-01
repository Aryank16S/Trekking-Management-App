from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from models import db, Trek, Booking, User, FitnessData
from ml.recommender import recommender
from ml.fitness_predictor import fitness_predictor
from ml.demand_forecaster import demand_forecaster
from ml.assistant import ai_assistant
from ml.watch_sync import watch_sync_engine

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai/matchmaker", methods=["GET", "POST"])
def matchmaker():
    """
    Personalized AI Trek Matchmaker using ML feature vectorization and cosine similarity.
    """
    all_treks = Trek.query.all()
    recommendations = []
    submitted = False
    fitness_level = "Intermediate"
    budget = 10000
    duration = 6
    terrain = "All"

    if request.method == "POST":
        submitted = True
        fitness_level = request.form.get("fitness_level", "Intermediate")
        try:
            budget = float(request.form.get("budget", 10000))
        except (ValueError, TypeError):
            budget = 10000

        try:
            duration = int(request.form.get("duration", 6))
        except (ValueError, TypeError):
            duration = 6

        terrain = request.form.get("terrain", "All")

        recommendations = recommender.recommend_for_user_preferences(
            all_treks=all_treks,
            fitness_level=fitness_level,
            max_budget=budget,
            max_duration=duration,
            terrain_pref=terrain,
            top_n=6
        )

    return render_template(
        "ai/matchmaker.html",
        recommendations=recommendations,
        submitted=submitted,
        fitness_level=fitness_level,
        budget=budget,
        duration=duration,
        terrain=terrain,
        all_treks=all_treks
    )

@ai_bp.route("/ai/readiness", methods=["GET", "POST"])
def readiness():
    """
    ML Fitness Readiness & Risk Assessment for a specific trek.
    Auto-ingests Smartwatch biometrics (VO2 Max, Resting HR, Elevation, SpO2) if available.
    """
    all_treks = Trek.query.all()
    assessment = None
    selected_trek = None
    age = 25
    weekly_exercise = 4.0
    prior_treks = 1
    high_alt_exp = False
    has_medical = False

    # Check for connected smartwatch telemetry
    watch_data = None
    if current_user.is_authenticated:
        watch_data = current_user.latest_fitness_data
        if watch_data and watch_data.weekly_active_hours:
            weekly_exercise = round(watch_data.weekly_active_hours, 1)

    preselected_trek_id = request.args.get("trek_id")
    if preselected_trek_id:
        try:
            selected_trek = Trek.query.get(int(preselected_trek_id))
        except Exception:
            pass

    if request.method == "POST":
        try:
            age = int(request.form.get("age", 25))
            weekly_exercise = float(request.form.get("weekly_exercise", 4.0))
            prior_treks = int(request.form.get("prior_treks", 1))
            high_alt_exp = request.form.get("high_alt_exp") == "yes"
            has_medical = request.form.get("has_medical") == "yes"
            trek_id = request.form.get("trek_id")

            if trek_id:
                selected_trek = Trek.query.get(int(trek_id))

            diff = selected_trek.difficulty if selected_trek else "Moderate"
            dur = selected_trek.duration if selected_trek else 5

            # Pass smartwatch metrics if available
            rhr = watch_data.resting_heart_rate if watch_data else None
            vo2 = watch_data.vo2_max if watch_data else None
            spo2 = watch_data.spo2_pct if watch_data else None
            ele = watch_data.elevation_gain_m if watch_data else None
            dev = watch_data.device_source if watch_data else None

            assessment = fitness_predictor.predict(
                age=age,
                weekly_exercise=weekly_exercise,
                prior_treks=prior_treks,
                high_alt_exp=high_alt_exp,
                has_medical=has_medical,
                difficulty=diff,
                duration=dur,
                resting_heart_rate=rhr,
                vo2_max=vo2,
                spo2_pct=spo2,
                elevation_gain_m=ele,
                device_source=dev
            )
        except Exception as e:
            flash(f"Error computing readiness assessment: {e}", "danger")

    return render_template(
        "ai/readiness.html",
        all_treks=all_treks,
        selected_trek=selected_trek,
        assessment=assessment,
        age=age,
        weekly_exercise=weekly_exercise,
        prior_treks=prior_treks,
        high_alt_exp=high_alt_exp,
        has_medical=has_medical,
        watch_data=watch_data
    )

@ai_bp.route("/ai/watch-sync")
@login_required
def watch_sync():
    """
    Dedicated Smartwatch Health & Fitness Hub:
    Allows user to transfer data from Apple Watch, Garmin, Strava, Fitbit,
    Samsung Health, or direct Web Bluetooth.
    """
    latest_data = current_user.latest_fitness_data
    records = current_user.fitness_records[:5] if current_user.fitness_records else []
    return render_template(
        "ai/watch_sync.html",
        latest_data=latest_data,
        records=records
    )

@ai_bp.route("/api/watch/upload", methods=["POST"])
@login_required
def api_watch_upload():
    """
    API: Ingests GPX, TCX, CSV, or JSON file directly exported from any fitness watch.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"success": False, "error": "Empty file"}), 400

    try:
        metrics = watch_sync_engine.process_upload(file)

        # Store in database linked to user
        record = FitnessData(
            user_id=current_user.id,
            device_source=metrics["device_source"],
            avg_heart_rate=metrics.get("avg_heart_rate"),
            resting_heart_rate=metrics.get("resting_heart_rate"),
            max_heart_rate=metrics.get("max_heart_rate"),
            vo2_max=metrics.get("vo2_max"),
            weekly_active_hours=metrics.get("weekly_active_hours"),
            daily_steps=metrics.get("daily_steps"),
            elevation_gain_m=metrics.get("elevation_gain_m"),
            distance_km=metrics.get("distance_km"),
            calories_burned=metrics.get("calories_burned"),
            spo2_pct=metrics.get("spo2_pct"),
            raw_filename=metrics.get("raw_filename")
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Successfully synced data from {metrics['device_source']}!",
            "metrics": metrics
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@ai_bp.route("/api/watch/sync-preset", methods=["POST"])
@login_required
def api_watch_sync_preset():
    """
    API: One-click quick cloud sync simulation for major fitness watches.
    """
    data = request.get_json() or {}
    brand = data.get("brand", "Garmin")
    metrics = watch_sync_engine.generate_preset(brand)

    record = FitnessData(
        user_id=current_user.id,
        device_source=metrics["device_source"],
        avg_heart_rate=metrics.get("avg_heart_rate"),
        resting_heart_rate=metrics.get("resting_heart_rate"),
        max_heart_rate=metrics.get("max_heart_rate"),
        vo2_max=metrics.get("vo2_max"),
        weekly_active_hours=metrics.get("weekly_active_hours"),
        daily_steps=metrics.get("daily_steps"),
        elevation_gain_m=metrics.get("elevation_gain_m"),
        distance_km=metrics.get("distance_km"),
        calories_burned=metrics.get("calories_burned"),
        spo2_pct=metrics.get("spo2_pct"),
        raw_filename=metrics.get("raw_filename")
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Successfully connected and synced with {metrics['device_source']}!",
        "metrics": metrics
    })

@ai_bp.route("/api/watch/bluetooth-save", methods=["POST"])
@login_required
def api_watch_bluetooth_save():
    """
    API: Receives live telemetry streamed directly from Web Bluetooth in the browser.
    """
    data = request.get_json() or {}
    device_name = data.get("device_name", "Bluetooth Smartwatch")
    hr = float(data.get("heart_rate", 72.0))
    resting_hr = float(data.get("resting_heart_rate", max(50.0, hr - 20.0)))
    vo2_max = float(data.get("vo2_max", 48.0))
    weekly_hours = float(data.get("weekly_active_hours", 5.5))
    steps = int(data.get("steps", 10000))
    elevation = float(data.get("elevation_gain_m", 300.0))

    record = FitnessData(
        user_id=current_user.id,
        device_source=f"Web Bluetooth ({device_name})",
        avg_heart_rate=hr,
        resting_heart_rate=resting_hr,
        max_heart_rate=hr + 35.0,
        vo2_max=vo2_max,
        weekly_active_hours=weekly_hours,
        daily_steps=steps,
        elevation_gain_m=elevation,
        distance_km=round(steps * 0.00075, 2),
        calories_burned=round(weekly_hours * 480.0, 1),
        spo2_pct=98.0,
        raw_filename="BLE_GATT_Stream.json"
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Connected to {device_name} over Bluetooth! Biometrics saved.",
        "metrics": {
            "device_source": f"Web Bluetooth ({device_name})",
            "avg_heart_rate": hr,
            "resting_heart_rate": resting_hr,
            "vo2_max": vo2_max,
            "weekly_active_hours": weekly_hours,
            "daily_steps": steps,
            "elevation_gain_m": elevation
        }
    })

@ai_bp.route("/ai/assistant")
def assistant():
    """
    Interactive AI Trekking Assistant interface.
    """
    all_treks = Trek.query.all()
    return render_template("ai/assistant.html", all_treks=all_treks)

@ai_bp.route("/api/ai/chat", methods=["POST"])
def api_chat():
    """
    JSON API endpoint for TrekBot conversations.
    """
    data = request.get_json() or {}
    user_msg = data.get("message", "")
    all_treks = Trek.query.all()
    reply = ai_assistant.chat_response(user_msg, all_treks)
    return jsonify({"reply": reply})

@ai_bp.route("/api/ai/packing/<int:trek_id>")
def api_packing(trek_id):
    """
    JSON API endpoint to get customized packing checklist for a trek.
    """
    trek = Trek.query.get_or_404(trek_id)
    checklist = ai_assistant.generate_packing_list(trek.name, trek.duration, trek.difficulty)
    return jsonify(checklist)

@ai_bp.route("/api/ai/itinerary/<int:trek_id>")
def api_itinerary(trek_id):
    """
    JSON API endpoint to get day-by-day itinerary plan for a trek.
    """
    trek = Trek.query.get_or_404(trek_id)
    plan = ai_assistant.generate_itinerary(trek.name, trek.location, trek.duration, trek.difficulty)
    return jsonify(plan)

@ai_bp.route("/admin/ai-analytics")
@login_required
def admin_ai_analytics():
    """
    Admin ML Dashboard: Demand forecasting, capacity fill rates, and dynamic pricing advice.
    """
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.home"))

    all_treks = Trek.query.all()
    analytics = demand_forecaster.analyze_treks(all_treks)
    return render_template("admin/ai_analytics.html", analytics=analytics)
