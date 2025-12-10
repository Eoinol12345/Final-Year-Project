import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import LogEntry, MealPreset

# create Flask app context so SQLAlchemy works
app = create_app()

with app.app_context():
    print("🌱 Seeding PancrePal database ...")

    # Clear old data
    db.session.query(LogEntry).delete()
    db.session.query(MealPreset).delete()
    db.session.commit()

    meals = [
        "Porridge", "Chicken Wrap", "Pasta", "Salad", "Yoghurt",
        "Toast", "Snack Bar", "Rice", "Omelette", "Cereal"
    ]
    moods = ["😊", "😐", "😞", ""]
    times = ["Breakfast", "Lunch", "Dinner", "Snack", "Training"]

    today = datetime.utcnow().date()

    # Create 7 days of data, 10 entries per day
    for d in range(7):
        date = today - timedelta(days=6 - d)
        for _ in range(10):
            entry = LogEntry(
                glucose=round(random.uniform(4.5, 12.5), 1),
                meal=random.choice(meals),
                mood=random.choice(moods),
                time_of_day=random.choice(times),
                noted_at=datetime.combine(date, datetime.min.time())
                    + timedelta(hours=random.randint(6, 22),
                                minutes=random.randint(0, 59))
            )
            db.session.add(entry)

    db.session.commit()
    print("✅ Seed complete — 70 entries added (10 per day, 7 days).")
