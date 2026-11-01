import os
import sys

# Ensure the app directory is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp
from routes.ai import ai_bp
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

# Ensure uploads directory exists
upload_folder = app.config.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "static", "uploads"))
os.makedirs(upload_folder, exist_ok=True)

db.init_app(app)

# Register application blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)
app.register_blueprint(ai_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # type:ignore

with app.app_context():
    db.create_all()

    admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    if admin_email and admin_password:
        admin = User.query.filter_by(email=admin_email).first()

        if not admin:
            admin = User(
                name="Admin",
                email=admin_email,
                password=generate_password_hash(admin_password),
                role="admin",
                approved=True,
                blacklisted=False
            )
            db.session.add(admin)
            db.session.commit()
        else:
            # Synchronize password with environment configuration
            admin.password = generate_password_hash(admin_password)
            admin.role = "admin"
            admin.approved = True
            admin.blacklisted = False
            db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
