def drought_risk(gwl):
    if gwl < -40:
        return "Severe Drought"
    elif gwl < -30:
        return "Drought"
    elif gwl < -20:
        return "Warning"
    else:
        return "Normal"
