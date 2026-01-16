import numpy as np

def create_sequences(X, y, seq_len=30):
    Xs, ys = [], []
    for i in range(len(X) - seq_len):
        Xs.append(X[i:i+seq_len])
        ys.append(y[i+seq_len])
    return np.array(Xs), np.array(ys)

DEPLOYABLE_WELLS = {
    "Bad_dhamsya": 0.54,
    "Shri_jagdishpura": 0.90
}


def drought_risk(gwl):
    """
    Simple, interpretable drought risk classification
    """
    depth = abs(gwl)

    if gwl < 5:
        return "Normal"
    elif gwl < 10:
        return "Watch"
    elif gwl < 15:
        return "Warning"
    else:
        return "Drought"