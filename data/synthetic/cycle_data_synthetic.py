"""
Generate synthetic BBT (Basal Body Temperature) cycle data.
Mimics the structure of NaturalCycles exported data.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

np.random.seed(42)
random.seed(42)

# --- Config ---
START_DATE = date(2021, 4, 1)
END_DATE = date(2026, 4, 1)
AVG_CYCLE_LENGTH = 28
CYCLE_STD = 2.5

# Data flags
PAIN_FLAGS = ["PAIN_CRAMPS", "PAIN_HEADACHE", "PAIN_BACKACHE", "PAIN_SORE_BREASTS", "PAIN_OVULATION"]
MOOD_FLAGS = ["MOOD_HAPPY", "MOOD_ENERGETIC", "MOOD_SENSITIVE", "MOOD_SAD", "MOOD_STRESSED",
              "MOOD_ANXIOUS", "MOOD_PMS", "MOOD_SWINGS", "MOOD_IRRITABLE"]
DEVIATION_FLAGS = ["DEVIATION_REASON_SLEEP", "DEVIATION_REASON_ALCOHOL", "DEVIATION_REASON_FEVER"]
CERVICAL_FLAGS = ["EGGWHITE", "CREAMY", "STICKY", "WATERY"]
WITHDRAWAL_FLAGS = ["WITHDRAWAL", "NO_WITHDRAWAL"]


def generate_cycle_temperatures(cycle_length, follicular_mean=36.35, luteal_mean=36.65):
    """Generate BBT temperatures for one cycle with realistic patterns."""
    temps = []
    ovulation_day = int(cycle_length * 0.45) + np.random.randint(-2, 3)

    for day in range(cycle_length):
        if day < ovulation_day:
            # Follicular phase - lower temps
            base = follicular_mean + np.random.normal(0, 0.08)
        elif day == ovulation_day:
            # Ovulation dip
            base = follicular_mean - 0.1 + np.random.normal(0, 0.05)
        else:
            # Luteal phase - higher temps
            base = luteal_mean + np.random.normal(0, 0.08)

        # Occasionally skip measurement (~15% of days)
        if random.random() < 0.15:
            temps.append(None)
        else:
            temps.append(round(base, 2))

    return temps, ovulation_day


def random_flags(flag_list, prob=0.3, max_flags=3):
    """Randomly pick flags from a list."""
    selected = [f for f in flag_list if random.random() < prob]
    return ",".join(selected[:max_flags]) if selected else None


def generate_data():
    rows = []
    current_date = START_DATE

    while current_date < END_DATE:
        cycle_length = max(21, min(35, int(np.random.normal(AVG_CYCLE_LENGTH, CYCLE_STD))))
        temps, ovulation_day = generate_cycle_temperatures(cycle_length)

        for day_num, temp in enumerate(temps):
            if current_date >= END_DATE:
                break

            is_menstruation = day_num < 5  # First 5 days of cycle
            is_near_ovulation = abs(day_num - ovulation_day) <= 2
            is_luteal = day_num > ovulation_day

            # Build data flags
            flags = []
            if is_menstruation and random.random() < 0.6:
                flags.append(random.choice(["PAIN_CRAMPS", "PAIN_HEADACHE", "PAIN_BACKACHE"]))
            if is_luteal and random.random() < 0.3:
                flags.append(random.choice(["MOOD_PMS", "MOOD_SWINGS", "MOOD_IRRITABLE", "PAIN_SORE_BREASTS"]))
            if random.random() < 0.15:
                flags.append(random.choice(MOOD_FLAGS))
            if random.random() < 0.05:
                flags.append(random.choice(DEVIATION_FLAGS))

            # Cervical mucus
            if is_near_ovulation:
                cervical = random.choice(["EGGWHITE", "WATERY"])
                cervical_qty = random.choice(["HEAVY", "MEDIUM"])
            elif is_luteal:
                cervical = random.choice(["CREAMY", "STICKY", None])
                cervical_qty = random.choice(["MEDIUM", "LOW", None])
            else:
                cervical = random.choice(["CREAMY", None, None])
                cervical_qty = random.choice(["LOW", None, None])

            row = {
                "Date": current_date.isoformat(),
                "Temperature": temp,
                "Menstruation": "MENSTRUATION" if is_menstruation else None,
                "LH test": None,
                "Pregnancy test": None,
                "Had sex": random.choice(["YES", "YES_PROTECTED", "NO", None, None, None]),
                "Notes": None,
                "Skipped": None,
                "Source": None,
                "Data Flag": ",".join(flags) if flags else None,
                "Menstruation Quantity": random.choice(["HEAVY", "MEDIUM", "LIGHT"]) if is_menstruation else None,
                "Cervical Mucus Consistency": cervical,
                "Cervical Mucus Quantity": cervical_qty,
            }
            rows.append(row)
            current_date += timedelta(days=1)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Generating synthetic cycle data...")
    df = generate_data()
    output_path = "data/synthetic/cycle_data_synthetic.csv"
    df.to_csv(output_path, index=False)
    print(f"Done! {len(df)} rows saved to {output_path}")
    print(df.head(10))