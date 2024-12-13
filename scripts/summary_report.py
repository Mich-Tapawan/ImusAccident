import numpy as np
import joblib
import os

def generate_summary_report(barangay):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "accident_prediction_model.pkl")
        encoder_path = os.path.join(current_dir, "barangay_encoder.pkl")

        model = joblib.load(model_path)
        encoder = joblib.load(encoder_path)
        barangays = encoder.categories_[0]  # List of barangays

        if barangay not in barangays:
            raise ValueError(f"Invalid barangay: {barangay}. Available barangays: {list(barangays)}")

        # Find the index of the barangay in the one-hot encoded categories
        barangay_idx = np.where(barangays == barangay)[0][0]

        predictions = []
        for hour in range(24):
            # Create a one-hot encoded input vector for the barangay
            input_data = np.zeros(len(barangays) + 2)
            input_data[barangay_idx] = 1  # Set the one-hot encoding for the barangay
            input_data[-2:] = [hour, 1 if 7 <= hour <= 9 or 17 <= hour <= 19 else 0]  # Hour and peak hour flag

            # Predict
            probs = model.predict_proba([input_data])
            predictions.append(round(probs[0][1] * 100, 2))  # Append percentage to the list

        # Peak and lowest accident hours
        peak_hour = np.argmax(predictions)
        lowest_hour = np.argmin(predictions)

        # Initialize Quarters (6-hour ranges)
        quarters = {
            "0-5": range(0, 6),   # Midnight to early morning
            "6-11": range(6, 12),  # Morning to noon
            "12-17": range(12, 18),# Afternoon to early evening
            "18-23": range(18, 24) # Evening to night
        }

        # Average accident probability for each quarter
        quarter_accidents = {
            quarter: round(
            np.mean([predictions[hour] for hour in hours]), 2
            )
            for quarter, hours in quarters.items()
        }

        # Peak and lowest accident quarters
        peak_quarter = max(quarter_accidents, key=quarter_accidents.get)
        lowest_quarter = min(quarter_accidents, key=quarter_accidents.get)

        return {
            "predictions": predictions,
            "peak_hour": peak_hour,
            "peak_quarter": peak_quarter,
            "lowest_hour": lowest_hour,
            "lowest_quarter": lowest_quarter,
        }

    except Exception as e:
        print(f"Error in generate_summary_report: {str(e)}")
        raise e

# Example usage
barangay_name = "ANABU II-A"
summary_report = generate_summary_report(barangay_name)
print("Predictions (Hourly Accident Probabilities):", summary_report["predictions"])
print("Peak Accident Hour:", summary_report["peak_hour"])
print("Peak Accident Quarter:", summary_report["peak_quarter"])
print("Lowest Accident Hour:", summary_report["lowest_hour"])
print("Lowest Accident Quarter:", summary_report["lowest_quarter"])
