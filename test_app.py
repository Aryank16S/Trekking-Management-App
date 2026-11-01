import os
import sys
import io

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if os.path.exists(os.path.join(BASE_DIR, "app.py")):
    APP_DIR = BASE_DIR
else:
    APP_DIR = os.path.join(BASE_DIR, "Trekking-Management-App")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import app
from models import db, User, Trek, Booking, FitnessData
from ml.recommender import recommender
from ml.fitness_predictor import fitness_predictor
from ml.demand_forecaster import demand_forecaster
from ml.assistant import ai_assistant
from ml.watch_sync import watch_sync_engine

def run_tests():
    print("=" * 60)
    print("      RUNNING TREKMATE SYSTEM & AI/ML TESTS         ")
    print("=" * 60)

    client = app.test_client()
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name}: {details}")

    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        # 1. Test Database Seeding & Models
        user_count = User.query.count()
        trek_count = Trek.query.count()
        assert_test("Database Models Loaded", user_count > 0 and trek_count > 0, f"Users: {user_count}, Treks: {trek_count}")

        # 2. Test Public Routes
        res_home = client.get("/")
        assert_test("Home Page Route (200 OK)", res_home.status_code == 200)

        res_about = client.get("/about")
        assert_test("About Page Route (200 OK)", res_about.status_code == 200)

        res_contact = client.get("/contact")
        assert_test("Contact Page Route (200 OK)", res_contact.status_code == 200)

        # 3. Test AI Matchmaker GET & POST
        res_match_get = client.get("/ai/matchmaker")
        assert_test("AI Matchmaker GET (200 OK)", res_match_get.status_code == 200)

        res_match_post = client.post("/ai/matchmaker", data={
            "fitness_level": "Intermediate",
            "budget": "10000",
            "duration": "6",
            "terrain": "Snow"
        })
        assert_test("AI Matchmaker POST (200 OK)", res_match_post.status_code == 200 and b"Top AI Recommendations" in res_match_post.data)

        # 4. Test AI Fitness Readiness GET & POST
        trek = Trek.query.first()
        res_read_get = client.get(f"/ai/readiness?trek_id={trek.id}")
        assert_test("AI Readiness GET (200 OK)", res_read_get.status_code == 200)

        res_read_post = client.post("/ai/readiness", data={
            "age": "26",
            "weekly_exercise": "5",
            "prior_treks": "2",
            "high_alt_exp": "yes",
            "has_medical": "",
            "trek_id": str(trek.id)
        })
        assert_test("AI Readiness POST Evaluator", res_read_post.status_code == 200 and b"Physical Readiness Index" in res_read_post.data)

        # 5. Test TrekBot Chat API
        res_chat = client.post("/api/ai/chat", json={"message": "How to prevent altitude sickness AMS?"})
        assert_test("TrekBot Chat API (200 OK)", res_chat.status_code == 200 and "AMS" in res_chat.get_json().get("reply", ""))

        # 6. Test AI Packing Checklist API
        res_pack = client.get(f"/api/ai/packing/{trek.id}")
        pack_data = res_pack.get_json()
        assert_test("AI Packing API", res_pack.status_code == 200 and "Clothing & Layering" in pack_data.get("categories", {}))

        # 7. Test AI Itinerary API
        res_itin = client.get(f"/api/ai/itinerary/{trek.id}")
        itin_data = res_itin.get_json()
        assert_test("AI Itinerary API", res_itin.status_code == 200 and len(itin_data.get("days", [])) > 0)

        # 8. Test Direct ML Recommender Logic
        all_treks = Trek.query.all()
        recs = recommender.recommend_for_user_preferences(all_treks, "Beginner", 5000, 3, "Fort", top_n=2)
        assert_test("ML Recommender Algorithm", len(recs) > 0 and "score" in recs[0])

        sims = recommender.get_similar_treks(trek, all_treks, top_n=2)
        assert_test("ML Content-Based Similar Treks", len(sims) > 0 and "score" in sims[0])

        # 9. Test Direct ML Fitness Predictor with Smartwatch Telemetry
        fit_res_base = fitness_predictor.predict(
            age=28, weekly_exercise=4.0, prior_treks=1, high_alt_exp=False,
            has_medical=False, difficulty="Moderate", duration=5
        )
        fit_res_watch = fitness_predictor.predict(
            age=28, weekly_exercise=4.0, prior_treks=1, high_alt_exp=False,
            has_medical=False, difficulty="Moderate", duration=5,
            resting_heart_rate=52.0, vo2_max=52.0, elevation_gain_m=650.0,
            device_source="Garmin Forerunner 965"
        )
        # Smartwatch telemetry should reflect enhanced readiness and biometrics applied
        assert_test("ML Fitness Predictor Smartwatch Integration",
                    fit_res_watch["readiness_pct"] > fit_res_base["readiness_pct"] and len(fit_res_watch["biometrics_applied"]) > 0)

        # 10. Test ML Demand Forecaster
        analytics = demand_forecaster.analyze_treks(all_treks)
        assert_test("ML Demand Forecaster Analytics", analytics["total_capacity"] > 0 and len(analytics["treks_data"]) == len(all_treks))

        # 11. Test Admin Login and Admin AI Analytics Route
        res_login_admin = client.post("/login", data={
            "email": "admin@gmail.com",
            "password": "admin123"
        }, follow_redirects=True)
        assert_test("Admin Login (200 OK)", res_login_admin.status_code == 200 and b"Welcome" in res_login_admin.data)

        res_analytics = client.get("/admin/ai-analytics")
        assert_test("Admin AI Analytics Page (200 OK)", res_analytics.status_code == 200 and b"Demand Forecasting" in res_analytics.data)

        # 12. Test User Login
        client.get("/logout")
        res_login_user = client.post("/login", data={
            "email": "user@gmail.com",
            "password": "user123"
        }, follow_redirects=True)
        assert_test("User Login (200 OK)", res_login_user.status_code == 200 and (b"User Dashboard" in res_login_user.data or b"Welcome" in res_login_user.data))

        # 13. Test Smartwatch Hub GET Route
        res_watch_get = client.get("/ai/watch-sync")
        assert_test("Smartwatch Hub Page GET (200 OK)", res_watch_get.status_code == 200 and b"Smartwatch Health" in res_watch_get.data)

        # 14. Test Smartwatch Cloud Preset Sync API
        res_preset = client.post("/api/watch/sync-preset", json={"brand": "Garmin"})
        preset_json = res_preset.get_json()
        assert_test("Smartwatch 1-Click Cloud Sync API", res_preset.status_code == 200 and preset_json.get("success") and "Garmin" in preset_json.get("message"))

        # 15. Test Smartwatch GPX File Upload API
        sample_gpx = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Apple Watch Ultra" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Morning Alpine Trail Run</name>
    <trkseg>
      <trkpt lat="30.123" lon="79.456"><ele>1850.0</ele><time>2026-10-26T06:00:00Z</time><extensions><gpxtpx:hr>132</gpxtpx:hr></extensions></trkpt>
      <trkpt lat="30.130" lon="79.462"><ele>2120.0</ele><time>2026-10-26T06:50:00Z</time><extensions><gpxtpx:hr>158</gpxtpx:hr></extensions></trkpt>
    </trkseg>
  </trk>
</gpx>"""
        data = {
            "file": (io.BytesIO(sample_gpx), "apple_watch_workout.gpx")
        }
        res_upload = client.post("/api/watch/upload", data=data, content_type="multipart/form-data")
        upload_json = res_upload.get_json()
        assert_test("Smartwatch GPX Upload & Parser API", res_upload.status_code == 200 and upload_json.get("success") and upload_json["metrics"]["elevation_gain_m"] > 0)

        # 16. Test Smartwatch Web Bluetooth Live Telemetry Save API
        res_bt = client.post("/api/watch/bluetooth-save", json={
            "device_name": "Garmin Fenix 7 Pro",
            "heart_rate": 70,
            "resting_heart_rate": 50,
            "vo2_max": 53.0,
            "weekly_active_hours": 7.0,
            "steps": 13000,
            "elevation_gain_m": 480
        })
        bt_json = res_bt.get_json()
        assert_test("Smartwatch Web Bluetooth Telemetry Save API", res_bt.status_code == 200 and bt_json.get("success"))

        # 17. Verify User's latest_fitness_data property
        user = User.query.filter_by(email="user@gmail.com").first()
        assert_test("User Model Fitness Telemetry Link", user.latest_fitness_data is not None and user.latest_fitness_data.resting_heart_rate == 50.0)

        # 18. Test Trek Booking Flow & Duplicate Prevention
        unbooked_trek = Trek.query.filter(Trek.id != trek.id).first()
        res_book = client.post(f"/user/book/{unbooked_trek.id}", follow_redirects=True)
        assert_test("Trek Booking Flow", res_book.status_code == 200)

        res_dup_book = client.post(f"/user/book/{unbooked_trek.id}", follow_redirects=True)
        assert_test("Duplicate Booking Prevention", b"already booked" in res_dup_book.data or b"info" in res_dup_book.data)

        # 19. Test Trek Photo Slides Property
        assert_test("Trek Photo Slides (3+ images)", len(trek.gallery_images) >= 3 and all(img.startswith("http") for img in trek.gallery_images))

        # 20. Test 24-Hour Login Limit (Max 3 Logins & Admin Control)
        # Create test demo user
        test_user = User.query.filter_by(email="limit_test@example.com").first()
        if not test_user:
            from werkzeug.security import generate_password_hash
            test_user = User(
                name="Limit Tester",
                email="limit_test@example.com",
                password=generate_password_hash("pass123"),
                role="user",
                approved=True,
                blacklisted=False
            )
            db.session.add(test_user)
            db.session.commit()

        test_user.reset_login_limit()
        db.session.commit()

        # Login 1
        client.get("/logout")
        res_l1 = client.post("/login", data={"email": "limit_test@example.com", "password": "pass123"}, follow_redirects=True)
        # Login 2
        client.get("/logout")
        res_l2 = client.post("/login", data={"email": "limit_test@example.com", "password": "pass123"}, follow_redirects=True)
        # Login 3
        client.get("/logout")
        res_l3 = client.post("/login", data={"email": "limit_test@example.com", "password": "pass123"}, follow_redirects=True)

        # 4th login attempt within 24h should be locked
        client.get("/logout")
        res_l4 = client.post("/login", data={"email": "limit_test@example.com", "password": "pass123"}, follow_redirects=True)
        assert_test("24-Hour 3-Login Limit Enforcement", b"Login limit reached" in res_l4.data or test_user.is_login_locked)

        # Admin unlocks user
        client.post("/login", data={"email": "admin@gmail.com", "password": "admin123"}, follow_redirects=True)
        res_unlock = client.post(f"/admin/users/reset-login/{test_user.id}", follow_redirects=True)
        assert_test("Admin Reset/Unlock Login Limit", res_unlock.status_code == 200 and not test_user.is_login_locked)

        # After unlock, user can log in again
        client.get("/logout")
        res_unlocked_login = client.post("/login", data={"email": "limit_test@example.com", "password": "pass123"}, follow_redirects=True)
        assert_test("User Login After Admin Unlock", res_unlocked_login.status_code == 200 and b"Welcome Limit Tester" in res_unlocked_login.data)

    print("=" * 60)
    print(f" TEST RESULTS: {passed} / {total} TESTS PASSED ({round((passed/total)*100)}%)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
