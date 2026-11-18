def calculate_personalized_fvm(fvm, budget):
    if fvm is None or str(fvm).strip() == '':
        return None
    try:
        return round((float(fvm) * float(budget)) / 1000, 1)
    except (ValueError, TypeError):
        return None
