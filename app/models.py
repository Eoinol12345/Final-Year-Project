from . import db
from datetime import datetime

class LogEntry(db.Model):
    __tablename__ = "log_entries"
    id = db.Column(db.Integer, primary_key=True)
    glucose = db.Column(db.Numeric(5, 2), nullable=False)
    meal = db.Column(db.String(120))
    mood = db.Column(db.String(50))  # "😊", "😐", "😞" or ""
    time_of_day = db.Column(db.String(50))  # "Breakfast", "Lunch", etc. (optional)
    noted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def mood_score(self) -> int:
        # basic scoring so the avatar can react
        if self.mood == "😊":
            return 1
        if self.mood == "😞":
            return -1
        return 0  # "" or "😐"

class MealPreset(db.Model):
    __tablename__ = "meal_presets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)       # e.g. "Porridge"
    default_glucose = db.Column(db.Numeric(5, 2))          # optional convenience
    default_mood = db.Column(db.String(50))                # optional emoji
    default_time_of_day = db.Column(db.String(50))         # e.g. "Breakfast"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
