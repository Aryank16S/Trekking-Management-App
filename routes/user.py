from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Trek, Booking, db
from ml.recommender import recommender

user_bp = Blueprint("user", __name__)

@user_bp.route("/user/dashboard")
@login_required
def user_dashboard():
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.home"))
    
    # Show user's recent bookings and recommended treks
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    all_treks = Trek.query.all()
    
    # Get smart recommendations for user
    recommendations = recommender.recommend_for_user_preferences(
        all_treks=all_treks,
        fitness_level="Intermediate",
        max_budget=15000,
        max_duration=7,
        top_n=3
    )
    
    return render_template(
        "user/dashboard.html",
        bookings=bookings,
        recommendations=recommendations
    )

@user_bp.route("/user/treks")
@login_required
def user_treks():
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.home"))
    treks = Trek.query.all()
    return render_template("user/treks.html", treks=treks)

@user_bp.route("/user/book/<int:trek_id>", methods=["POST"])
@login_required
def book_trek(trek_id):
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.home"))
    
    trek = Trek.query.get_or_404(trek_id)

    # Prevent duplicate booking
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).first()
    if existing_booking:
        flash("You have already booked this trek! Check your bookings below.", "info")
        return redirect(url_for("user.my_bookings"))

    # Check participant capacity
    current_bookings_count = Booking.query.filter_by(trek_id=trek.id).count()
    if current_bookings_count >= trek.max_participants:
        flash(f"Sorry, '{trek.name}' is already at full capacity ({trek.max_participants} participants).", "warning")
        return redirect(url_for("user.user_treks"))

    booking = Booking(user_id=current_user.id, trek_id=trek.id)  # type: ignore
    db.session.add(booking)
    db.session.commit()
    flash(f"Trek '{trek.name}' booked successfully!", "success")
    return redirect(url_for("user.my_bookings"))

@user_bp.route("/user/bookings")
@login_required
def my_bookings():
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.home"))
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("user/bookings.html", bookings=bookings)

@user_bp.route("/user/bookings/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    if current_user.role != "user":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.home"))
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash("You are not authorized to cancel this booking.", "danger")
        return redirect(url_for("user.my_bookings"))
    db.session.delete(booking)
    db.session.commit()
    flash("Booking cancelled successfully.", "success")
    return redirect(url_for("user.my_bookings"))
