import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from models import db, User, Trek, Booking, FitnessData
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        print("[*] Seeding TrekMate database...")
        db.create_all()

        # 1. Seed or Update Admin
        admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="Admin",
                email=admin_email,
                password=generate_password_hash(admin_pass),
                role="admin",
                approved=True,
                blacklisted=False,
                phone="+91 9876543210"
            )
            db.session.add(admin)
        else:
            admin.password = generate_password_hash(admin_pass)
            admin.approved = True
            admin.blacklisted = False

        # 2. Seed Certified Staff Members
        staff_data = [
            ("Tenzing Dorje", "tenzing@trekmate.com", "staff123", "+91 9811223344"),
            ("Rajesh Sharma", "rajesh@trekmate.com", "staff123", "+91 9822334455"),
            ("Priya Negi", "priya@trekmate.com", "staff123", "+91 9833445566")
        ]

        staff_users = []
        for name, email, password, phone in staff_data:
            staff_user = User.query.filter_by(email=email).first()
            if not staff_user:
                staff_user = User(
                    name=name,
                    email=email,
                    password=generate_password_hash(password),
                    role="staff",
                    approved=True,
                    blacklisted=False,
                    phone=phone
                )
                db.session.add(staff_user)
            staff_users.append(staff_user)

        # 3. Seed Demo Users
        users_data = [
            ("Aarav Mehta", "user@gmail.com", "user123", "+91 9711223344"),
            ("Sneha Roy", "sneha@gmail.com", "user123", "+91 9722334455"),
            ("Vikram Singh", "vikram@gmail.com", "user123", "+91 9733445566")
        ]
        demo_users = []
        for name, email, password, phone in users_data:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    name=name,
                    email=email,
                    password=generate_password_hash(password),
                    role="user",
                    approved=True,
                    blacklisted=False,
                    phone=phone
                )
                db.session.add(user)
            demo_users.append(user)

        db.session.commit()

        # Reload staff users with IDs
        staff_users = User.query.filter_by(role="staff").all()
        demo_users = User.query.filter_by(role="user").all()

        # 4. Seed Diverse Treks (Himalayas & Western Ghats across difficulties)
        treks_data = [
            {
                "name": "Kedarkantha Winter Summit",
                "location": "Sankri, Uttarakhand",
                "difficulty": "Easy",
                "duration": 5,
                "price": 8500.0,
                "max_participants": 20,
                "description": "One of India's most popular winter snow summits at 12,500 ft. Features mesmerizing pine forest trails, frozen Juda Ka Talab lake, and 360-degree panoramic views of Himalayan giants including Swargarohini, Bandarpoonch, and Black Peak.",
                "staff_id": staff_users[0].id if staff_users else None
            },
            {
                "name": "Valley of Flowers & Hemkund Sahib",
                "location": "Chamoli, Uttarakhand",
                "difficulty": "Moderate",
                "duration": 6,
                "price": 10500.0,
                "max_participants": 18,
                "description": "UNESCO World Heritage site nestled in the Garhwal Himalayas. Carpets of hundreds of wild alpine flowers, rare orchids, and cascading glacial streams, followed by an ascent to the sacred glacial Hemkund Sahib lake at 14,100 ft.",
                "staff_id": staff_users[1].id if len(staff_users) > 1 else None
            },
            {
                "name": "Hampta Pass & Chandratal Lake",
                "location": "Manali, Himachal Pradesh",
                "difficulty": "Moderate",
                "duration": 5,
                "price": 9800.0,
                "max_participants": 16,
                "description": "A dramatic dramatic pass-crossing trek transitioning from the lush green pine valleys of Kullu to the stark, arid, moon-like high desert landscapes of Spiti Valley, concluding at the crescent-shaped blue waters of Chandratal.",
                "staff_id": staff_users[2].id if len(staff_users) > 2 else None
            },
            {
                "name": "Kudremukh Peak Expedition",
                "location": "Chikmagalur, Karnataka",
                "difficulty": "Easy",
                "duration": 2,
                "price": 3400.0,
                "max_participants": 25,
                "description": "A breathtaking Western Ghats biodiversity hotspot with lush rolling green hills, dense shola forest patches, and horse-faced mountain summit at 6,200 ft with cool mist and rolling clouds.",
                "staff_id": staff_users[0].id if staff_users else None
            },
            {
                "name": "Harishchandragad Konkan Kada",
                "location": "Ahmednagar, Maharashtra",
                "difficulty": "Moderate",
                "duration": 2,
                "price": 2800.0,
                "max_participants": 30,
                "description": "Historic hill fort trek dating back to the 6th century. Features ancient caves, Kedareshwar temple carved in rock, and the vertigo-inducing vertical concave cliff of Konkan Kada offering sunset cloud inversions.",
                "staff_id": staff_users[1].id if len(staff_users) > 1 else None
            },
            {
                "name": "Roopkund Mystery Lake Trek",
                "location": "Garhwal, Uttarakhand",
                "difficulty": "Hard",
                "duration": 8,
                "price": 14500.0,
                "max_participants": 12,
                "description": "High-altitude glacial expedition taking you through India's twin twin green meadows Ali and Bedni Bugyal up to the high ridge of 15,750 ft, surrounded by towering peaks of Trishul and Nanda Ghunti.",
                "staff_id": staff_users[0].id if staff_users else None
            },
            {
                "name": "Brahmatal Frozen Lake Trail",
                "location": "Lohajung, Uttarakhand",
                "difficulty": "Moderate",
                "duration": 6,
                "price": 9200.0,
                "max_participants": 18,
                "description": "An unmatched snow trail offering front-row amphitheater views of Mt. Trishul and Nanda Ghunti. Walk along serene snow-covered oak woods and camp beside the mystical frozen alpine lake of Brahmatal.",
                "staff_id": staff_users[2].id if len(staff_users) > 2 else None
            },
            {
                "name": "Chadar Frozen Zanskar River Expedition",
                "location": "Leh, Ladakh",
                "difficulty": "Hard",
                "duration": 9,
                "price": 28500.0,
                "max_participants": 10,
                "description": "The ultimate extreme sub-zero Himalayan challenge. Walk on the thick glass-like ice sheet of the frozen Zanskar river through steep canyons with frozen waterfalls in bone-chilling minus 25 degree temperatures.",
                "staff_id": staff_users[0].id if staff_users else None
            }
        ]

        seeded_treks = []
        for t_info in treks_data:
            existing = Trek.query.filter_by(name=t_info["name"]).first()
            if not existing:
                trek = Trek(**t_info)
                db.session.add(trek)
                seeded_treks.append(trek)
            else:
                seeded_treks.append(existing)

        db.session.commit()

        # 5. Seed Realistic Sample Bookings
        if demo_users and seeded_treks:
            # Let's add bookings for demo users across first few treks
            sample_bookings = [
                (demo_users[0].id, seeded_treks[0].id),
                (demo_users[1].id, seeded_treks[0].id),
                (demo_users[0].id, seeded_treks[1].id),
                (demo_users[2].id, seeded_treks[2].id),
                (demo_users[1].id, seeded_treks[3].id),
                (demo_users[2].id, seeded_treks[0].id),
            ]
            for u_id, tr_id in sample_bookings:
                existing_b = Booking.query.filter_by(user_id=u_id, trek_id=tr_id).first()
                if not existing_b:
                    b = Booking(user_id=u_id, trek_id=tr_id, status="Confirmed")
                    db.session.add(b)

            db.session.commit()

        # 6. Seed Sample Smartwatch Telemetry
        if demo_users:
            primary_user = demo_users[0]
            if not primary_user.fitness_records:
                sample_watch_log = FitnessData(
                    user_id=primary_user.id,
                    device_source="Garmin Forerunner 965 (Connect Telemetry)",
                    avg_heart_rate=136.0,
                    resting_heart_rate=54.0,
                    max_heart_rate=174.0,
                    vo2_max=50.5,
                    weekly_active_hours=6.5,
                    daily_steps=12400,
                    elevation_gain_m=580.0,
                    distance_km=10.2,
                    calories_burned=760.0,
                    spo2_pct=98.5,
                    raw_filename="Garmin_Trail_Ascent.gpx"
                )
                db.session.add(sample_watch_log)
                db.session.commit()

        print("[SUCCESS] Database successfully seeded with Admin, Staff, Users, Treks, Bookings, and Watch Telemetry!")

if __name__ == "__main__":
    seed_database()
