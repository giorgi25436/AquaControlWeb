from datetime import date, timedelta


def calculate_cycle(group, start_date, today=None):
    today = today or date.today()
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
    }


def format_date(value):
    return value.strftime("%d/%m/%Y")
