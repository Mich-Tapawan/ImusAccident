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

        predictions = {}
        for hour in range(1, 25):  # Adjust range to 1-24
            # Create a one-hot encoded input vector for the barangay
            input_data = np.zeros(len(barangays) + 2)
            input_data[barangay_idx] = 1  # Set the one-hot encoding for the barangay
            input_data[-2:] = [hour - 1, 1 if 7 <= (hour - 1) <= 9 or 17 <= (hour - 1) <= 19 else 0]  
            # Hour - 1 for model input, since range 1-24 corresponds to indices 0-23

            # Predict
            probs = model.predict_proba([input_data])
            
            # Use zero-padded string for hour key (e.g., "01", "02", "03", ...)
            hour_key = str(hour - 1).zfill(2)
            predictions[hour_key] = round(probs[0][1] * 100, 2)  # Add to dictionary with string hour key

        # Peak and lowest accident hours
        peak_hour = max(predictions, key=predictions.get)
        lowest_hour = min(predictions, key=predictions.get)

        # Initialize Quarters (6-hour ranges)
        quarters = {
            "1-6": range(1, 7),   # Midnight to early morning
            "7-12": range(7, 13),  # Morning to noon
            "13-18": range(13, 19),# Afternoon to early evening
            "19-23": range(19, 24) # Evening to night (fixed range)
        }

        # Average accident probability for each quarter
        quarter_accidents = {
            quarter: round(
            np.mean([predictions[str(hour).zfill(2)] for hour in hours]), 2
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
