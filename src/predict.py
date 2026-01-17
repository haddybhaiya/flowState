import os
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from src.utils import DEPLOYABLE_WELLS, drought_risk

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models", "lstm")
OUTPUT_DIR = os.path.join(BASE_DIR, "predictions")

SEQ_LEN = 30
FORECAST_DAYS = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)
FEATURES = [
    "rain", "rain_lag_7", "rain_lag_30",
    "cum_rain_30", "gwl_lag_1",
    "gwl_trend_30", "month_sin", "month_cos"
]
def predict_well(well_name):
    if well_name not in DEPLOYABLE_WELLS:
        raise ValueError(f"{well_name} not approved for deployment")

    print(f"🔮 Predicting for {well_name}")

    # Load data
    df = pd.read_csv(os.path.join(DATA_DIR, f"well_{well_name}.csv"))

    # Load model & scalers
    model = load_model(os.path.join(MODEL_DIR, f"{well_name}.keras"))
    scaler_X = joblib.load(os.path.join(MODEL_DIR, f"{well_name}_scaler_X.pkl"))
    scaler_y = joblib.load(os.path.join(MODEL_DIR, f"{well_name}_scaler_y.pkl"))

    # Prepare input
    X = df[FEATURES].values
    X_scaled = scaler_X.transform(X)

    last_seq = X_scaled[-SEQ_LEN:]
    last_seq = last_seq.reshape(1, SEQ_LEN, X.shape[1])

    predictions = []

    for _ in range(FORECAST_DAYS):
        pred_scaled = model.predict(last_seq, verbose=0)
        pred = scaler_y.inverse_transform(pred_scaled)[0][0]
        predictions.append(pred)

        # Update sequence (autoregressive)
        new_step = last_seq[0, -1, :].copy()
        new_step[FEATURES.index("gwl_lag_1")] = pred_scaled[0][0]

        last_seq = np.append(last_seq[:, 1:, :], [[new_step]], axis=1)

    return predictions
if __name__ == "__main__":
    wells = [
        f.replace("well_", "").replace(".csv", "")
        for f in os.listdir(DATA_DIR)
        if f.startswith("well_")
    ]

    for well in wells:
        if well not in DEPLOYABLE_WELLS:
            print(f"Skipping {well} (not approved)")
            continue

        preds = predict_well(well)
        out = pd.DataFrame({
        "day": list(range(1, FORECAST_DAYS + 1)),
        "predicted_gwl": preds
            })
        from src.drought import drought_risk
        out["risk"] = out["predicted_gwl"].apply(drought_risk)

        out.to_csv(
            os.path.join(OUTPUT_DIR, f"{well}_forecast.csv"),
            index=False
            )

        print(f"Saved forecast for {well}")
