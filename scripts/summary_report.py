import numpy as np
import joblib
import pandas as pd
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

        # Load dataset for aggregating per quarter data
        dataset_path = os.path.join(current_dir, "../traffic-incident.xlsx")
        df = pd.read_excel(dataset_path, sheet_name=None)
        df_combined = pd.concat(df.values(), ignore_index=True)

        # Ensure dataset has necessary columns
        df_combined['dateCommitted'] = pd.to_datetime(df_combined['dateCommitted'], errors='coerce')
        df_combined['month'] = df_combined['dateCommitted'].dt.month

        # Filter for the given barangay
        df_barangay = df_combined[df_combined['barangay'] == barangay]

        # Group by quarter
        df_barangay['quarter'] = pd.cut(
            df_barangay['month'],
            bins=[0, 3, 6, 9, 12],
            labels=["Jan-Mar", "Apr-Jun", "Jul-Sep", "Oct-Dec"],
            include_lowest=True
        )
        quarter_probs = df_barangay.groupby('quarter').size() / len(df_barangay)

        # Peak and lowest accident quarters
        peak_quarter = quarter_probs.idxmax()
        lowest_quarter = quarter_probs.idxmin()

        # Initialize predictions dictionary for hourly accidents
        predictions = {}
        barangay_idx = np.where(barangays == barangay)[0][0]
        for hour in range(24):
            input_data = np.zeros(len(barangays) + 2)
            input_data[barangay_idx] = 1
            input_data[-2:] = [hour, 1 if 7 <= hour <= 9 or 17 <= hour <= 19 else 0]

            probs = model.predict_proba([input_data])
            predictions[str(hour).zfill(2)] = round(probs[0][1] * 100, 2)

        peak_hour = max(predictions, key=predictions.get)
        lowest_hour = min(predictions, key=predictions.get)

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
