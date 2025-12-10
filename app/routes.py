from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime, timedelta
from sqlalchemy import func
from . import db
from .models import LogEntry, MealPreset

bp = Blueprint("routes", __name__)

@bp.route("/")
def home():
    # Recent entries for table
    entries = LogEntry.query.order_by(LogEntry.noted_at.desc()).limit(50).all()

    # Avatar: react to last few moods / latest entry
    latest = LogEntry.query.order_by(LogEntry.noted_at.desc()).first()
    recent = LogEntry.query.order_by(LogEntry.noted_at.desc()).limit(5).all()
    mood_sum = sum(e.mood_score() for e in recent)
    if latest and latest.mood == "😞":
        avatar = "😟"
        avatar_msg = "Looks like a tough one — you’ve got this."
    elif mood_sum >= 2:
        avatar = "😄"
        avatar_msg = "Nice consistency! Keep it going."
    elif mood_sum <= -2:
        avatar = "😕"
        avatar_msg = "Small steps are still progress."
    else:
        avatar = "🙂"
        avatar_msg = "You’re doing fine — one entry at a time."

    # Chart.js: past 7 days (group by date, average glucose)
    today = datetime.utcnow().date()
    start = today - timedelta(days=6)  # 7-day window
    # Build a dict with all dates to keep order even if missing data
    labels = [(start + timedelta(days=i)).strftime("%d %b") for i in range(7)]
    label_to_date = { (start + timedelta(days=i)) : labels[i] for i in range(7) }

    # Query averages by day
    rows = (
        db.session.query(func.date(LogEntry.noted_at).label("d"), func.avg(LogEntry.glucose))
        .filter(LogEntry.noted_at >= datetime.combine(start, datetime.min.time()))
        .group_by(func.date(LogEntry.noted_at))
        .all()
    )
    avg_map = { r[0]: float(r[1]) for r in rows }  # {date: avg}

    chart_values = []
    for i in range(7):
        d = start + timedelta(days=i)
        chart_values.append(avg_map.get(d, None))  # None -> gap on chart

    # Presets for quick logging
    presets = MealPreset.query.order_by(MealPreset.created_at.desc()).all()

    return render_template(
        "home.html",
        entries=entries,
        avatar=avatar,
        avatar_msg=avatar_msg,
        labels=labels,
        chart_values=chart_values,
        presets=presets,
    )

# ---------- CRUD: LogEntry ----------

# CREATE (from form, quick buttons, or JSON)
@bp.route("/entries", methods=["POST"])
def create_entry():
    data = request.form or request.json
    glucose = data.get("glucose")
    meal = data.get("meal", "")
    mood = data.get("mood", "")
    time_of_day = data.get("time_of_day", "")

    if not glucose:
        flash("Glucose is required", "error")
        return redirect(url_for("routes.home"))

    entry = LogEntry(
        glucose=glucose,
        meal=meal,
        mood=mood,
        time_of_day=time_of_day
    )
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for("routes.home"))

# READ (JSON)
@bp.route("/api/entries", methods=["GET"])
def list_entries():
    entries = LogEntry.query.order_by(LogEntry.noted_at.desc()).all()
    return jsonify([
        {
            "id": e.id,
            "glucose": float(e.glucose),
            "meal": e.meal,
            "mood": e.mood,
            "time_of_day": e.time_of_day,
            "noted_at": e.noted_at.isoformat()
        } for e in entries
    ])

# UPDATE
@bp.route("/entries/<int:entry_id>", methods=["POST"])
def update_entry(entry_id):
    entry = LogEntry.query.get_or_404(entry_id)
    data = request.form or request.json
    if "glucose" in data and data.get("glucose") != "":
        entry.glucose = data.get("glucose")
    if "meal" in data:
        entry.meal = data.get("meal")
    if "mood" in data:
        entry.mood = data.get("mood")
    if "time_of_day" in data:
        entry.time_of_day = data.get("time_of_day")
    db.session.commit()
    return redirect(url_for("routes.home"))

# DELETE
@bp.route("/entries/<int:entry_id>/delete", methods=["POST"])
def delete_entry(entry_id):
    entry = LogEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("routes.home"))

# ---------- Meal Presets ----------

@bp.route("/presets", methods=["POST"])
def add_preset():
    data = request.form or request.json
    name = data.get("name", "").strip()
    default_glucose = data.get("default_glucose") or None
    default_mood = data.get("default_mood") or ""
    default_time = data.get("default_time_of_day") or ""
    if not name:
        flash("Preset name is required", "error")
        return redirect(url_for("routes.home"))
    preset = MealPreset(
        name=name,
        default_glucose=default_glucose,
        default_mood=default_mood,
        default_time_of_day=default_time
    )
    db.session.add(preset)
    db.session.commit()
    return redirect(url_for("routes.home"))

@bp.route("/presets/<int:preset_id>/use", methods=["POST"])
def use_preset(preset_id):
    preset = MealPreset.query.get_or_404(preset_id)
    # Create a log entry using preset defaults (glucose can be blank; allow user to edit after)
    entry = LogEntry(
        glucose=request.form.get("glucose") or preset.default_glucose or 0,
        meal=preset.name,
        mood=preset.default_mood or "",
        time_of_day=preset.default_time_of_day or ""
    )
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for("routes.home"))

@bp.route("/presets/<int:preset_id>/delete", methods=["POST"])
def delete_preset(preset_id):
    preset = MealPreset.query.get_or_404(preset_id)
    db.session.delete(preset)
    db.session.commit()
    return redirect(url_for("routes.home"))

# ---------- Privacy / Ethics ----------

@bp.route("/privacy")
def privacy():
    return render_template("privacy.html")
