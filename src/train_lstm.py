import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from utils import create_sequences
import os
well = "Bad_dhamsya"
df = pd.read_csv(f"data/processed/well_{well}.csv")

features = [
    "rain", "rain_lag_7", "rain_lag_30",
    "cum_rain_30", "gwl_lag_1",
    "gwl_trend_30", "month_sin", "month_cos"
]

X = df[features].values
y = df["gwl"].values
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))
SEQ_LEN = 30
X_seq, y_seq = create_sequences(X_scaled, y_scaled, SEQ_LEN)
split = int(0.8 * len(X_seq))
X_train, X_val = X_seq[:split], X_seq[split:]
y_train, y_val = y_seq[:split], y_seq[split:]
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(SEQ_LEN, X_seq.shape[2])),
    LSTM(32),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")
model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=[EarlyStopping(patience=5)],
    verbose=1
)
os.makedirs("models/lstm", exist_ok=True)
model.save(f"models/lstm/{well}.keras")
