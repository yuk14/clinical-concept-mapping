import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Step 1: Generate Dummy Data
np.random.seed(42)
data = {
    "Age": np.random.randint(20, 80, 500),
    "BloodPressure": np.random.randint(80, 180, 500),
    "Glucose": np.random.randint(70, 200, 500),
    "Cholesterol": np.random.randint(150, 300, 500),
    "HeartRate": np.random.randint(60, 120, 500),
    "RiskLevel": np.random.choice([0, 1], size=500)  # 0: Low Risk, 1: High Risk
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Step 2: Split Data into Features (X) and Target (y)
X = df[["Age", "BloodPressure", "Glucose", "Cholesterol", "HeartRate"]]
y = df["RiskLevel"]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 3: Train the Model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Step 4: Evaluate the Model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Step 5: Save the Trained Model
joblib.dump(model, "medical_model.pkl")
print("Model saved as 'medical_model.pkl'")
