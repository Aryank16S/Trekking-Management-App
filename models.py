from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")

    # 24-Hour Login Limit Control (Max 3 logins/attempts in 24 hours, controlled by Admin)
    login_count_24h = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_login_time = db.Column(db.DateTime, nullable=True)
    login_locked_until = db.Column(db.DateTime, nullable=True)
    login_blocked_by_admin = db.Column(db.Boolean, default=False)

    @property
    def is_login_locked(self):
        """
        Returns True if the user is currently locked from signing in.
        Admin users are exempt from login lockouts.
        """
        if self.role == "admin":
            return False

        if self.login_blocked_by_admin:
            return True

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        now_cmp = datetime.utcnow()

        # Check explicit lockout timestamp
        if self.login_locked_until:
            locked_until = self.login_locked_until
            check_now = now_cmp if locked_until.tzinfo is None else now
            if check_now < locked_until:
                return True

        # Check if 24 hours have passed since last login time
        if self.last_login_time:
            last = self.last_login_time
            check_now = now_cmp if last.tzinfo is None else now
            if (check_now - last).total_seconds() > 86400:
                return False

        # If 3 or more logins or failed attempts in active 24h window
        if (self.login_count_24h or 0) >= 3 or (self.failed_login_attempts or 0) >= 3:
            return True

        return False

    def record_login_attempt(self, successful=True):
        """
        Records a login attempt (successful or failed).
        Limits to 3 logins/attempts in 24 hours.
        """
        if self.role == "admin":
            return

        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        now_cmp = datetime.utcnow()

        # If more than 24 hours have passed, reset counters
        if self.last_login_time:
            last = self.last_login_time
            t_diff = (now_cmp - last).total_seconds() if last.tzinfo is None else (now - last).total_seconds()
            if t_diff > 86400:
                self.login_count_24h = 0
                self.failed_login_attempts = 0
                self.login_locked_until = None

        self.last_login_time = now

        if successful:
            self.login_count_24h = (self.login_count_24h or 0) + 1
            self.failed_login_attempts = 0
            if self.login_count_24h >= 3:
                self.login_locked_until = now + timedelta(hours=24)
        else:
            self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
            if self.failed_login_attempts >= 3:
                self.login_locked_until = now + timedelta(hours=24)

    def reset_login_limit(self):
        """Admin control: Resets login limits and unlocks user immediately."""
        self.login_count_24h = 0
        self.failed_login_attempts = 0
        self.login_locked_until = None
        self.login_blocked_by_admin = False

    @property
    def latest_fitness_data(self):
        """Returns the most recent smartwatch sync record."""
        return self.fitness_records[0] if self.fitness_records else None

class Trek(db.Model):
    __tablename__ = "treks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    bookings = db.relationship("Booking", backref="trek", lazy=True, cascade="all, delete-orphan")
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    staff = db.relationship("User", foreign_keys=[staff_id])

    @property
    def booked_count(self):
        return len(self.bookings) if self.bookings else 0

    @property
    def available_slots(self):
        return max(0, self.max_participants - self.booked_count)

    @property
    def gallery_images(self):
        """
        Returns an ordered list of high-definition slide photos for this trek.
        Includes uploaded custom images first, followed by curated scenic photography.
        """
        curated_galleries = {
            "kedarkantha": [
                "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80"
            ],
            "valley of flowers": [
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=80"
            ],
            "hampta": [
                "https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80"
            ],
            "kudremukh": [
                "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1434394354979-a235cd36269d?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80"
            ],
            "harishchandragad": [
                "https://images.unsplash.com/photo-1508873696983-2df5293cb32f?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?auto=format&fit=crop&w=800&q=80"
            ],
            "roopkund": [
                "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?auto=format&fit=crop&w=800&q=80"
            ],
            "brahmatal": [
                "https://images.unsplash.com/photo-1485470733090-0aae1788d5af?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=800&q=80"
            ],
            "chadar": [
                "https://images.unsplash.com/photo-1482867996988-29ec3a0f1aac?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1487147264018-f937fec0c844?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1510312305653-8ed496efae75?auto=format&fit=crop&w=800&q=80"
            ]
        }

        slides = []
        if self.image:
            from flask import url_for
            slides.append(url_for('static', filename='uploads/' + self.image))

        name_lower = (self.name or "").lower()
        matched = False
        for key, urls in curated_galleries.items():
            if key in name_lower:
                slides.extend(urls)
                matched = True
                break

        if not matched:
            slides.extend([
                "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80"
            ])

        return slides

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default="Confirmed", nullable=False)

class FitnessData(db.Model):
    """
    Stores biometric & telemetry records transferred directly from user's
    fitness smartwatch (Garmin, Apple Watch, Strava GPX/TCX, Fitbit, Web Bluetooth).
    """
    __tablename__ = "fitness_data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    device_source = db.Column(db.String(100), default="Smartwatch")
    sync_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Biometrics & activity metrics
    avg_heart_rate = db.Column(db.Float, nullable=True)        # BPM
    resting_heart_rate = db.Column(db.Float, nullable=True)    # BPM
    max_heart_rate = db.Column(db.Float, nullable=True)        # BPM
    vo2_max = db.Column(db.Float, nullable=True)               # ml/kg/min
    weekly_active_hours = db.Column(db.Float, nullable=True)   # Cardio workout hours
    daily_steps = db.Column(db.Integer, nullable=True)         # Steps count
    elevation_gain_m = db.Column(db.Float, nullable=True)      # Meters climbed
    distance_km = db.Column(db.Float, nullable=True)           # Distance in km
    calories_burned = db.Column(db.Float, nullable=True)       # kcal
    spo2_pct = db.Column(db.Float, nullable=True)              # Blood oxygen % (90-100)
    raw_filename = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", backref=db.backref("fitness_records", lazy=True, cascade="all, delete-orphan", order_by="desc(FitnessData.sync_date)"))
