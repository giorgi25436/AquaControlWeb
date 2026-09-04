from datetime import date, timedelta


def calculate_cycle(
    group,
    start_date,
    today=None,
    mode="Automatico",
    manual_start=None,
    manual_return=None,
):
    today = today or date.today()
    if mode == "Forzar LABORANDO" and (not manual_start or today >= manual_start):
        return {
            "name": group, "status": "LABORANDO", "is_resting": False,
            "day_label": "Estado manual", "days_to_transition": None,
            "next_exit": date.max, "next_return": date.max, "progress": 100,
            "start_date": start_date, "mode": mode, "is_manual": True,
            "manual_start": manual_start,
        }
    if mode == "Forzar EN DESCANSO" and (not manual_start or today >= manual_start):
        return_date = manual_return or (manual_start + timedelta(days=8))
        if today < return_date:
            day_number = (today - manual_start).days + 1
            return {
                "name": group, "status": "EN DESCANSO", "is_resting": True,
                "day_label": f"Día {min(day_number, 8)} de 8",
                "days_to_transition": (return_date - today).days,
                "next_exit": return_date, "next_return": return_date,
                "progress": round((min(day_number, 8) / 8) * 100),
                "start_date": start_date, "mode": mode, "is_manual": True,
                "manual_start": manual_start, "manual_return": return_date,
            }
    elapsed = (today - start_date).days
    day_index = elapsed % 30
    laboring = day_index < 22
    if laboring:
        day_number = day_index + 1
        days_to_transition = 22 - day_index
        next_exit = today + timedelta(days=days_to_transition)
        next_return = today + timedelta(days=30 - day_index)
        label = f"Día {day_number} de 22"
        status = "LABORANDO"
    else:
        rest_index = day_index - 22
        day_number = rest_index + 1
        days_to_transition = 30 - day_index
        next_exit = today + timedelta(days=22 + days_to_transition)
        next_return = today + timedelta(days=days_to_transition)
        label = f"Día {day_number} de 8"
        status = "EN DESCANSO"

    return {
        "name": group,
        "status": status,
        "is_resting": not laboring,
        "day_label": label,
        "days_to_transition": days_to_transition,
        "next_exit": next_exit,
        "next_return": next_return,
        "progress": round((day_number / (8 if not laboring else 22)) * 100),
        "start_date": start_date,
        "mode": "Automatico",
        "is_manual": False,
    }


def format_date(value):
    return value.strftime("%d/%m/%Y")
