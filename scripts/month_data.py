import pandas as pd

# Memoization dictionary to store precomputed totals
precomputed_totals = {}

def precompute_totals(FILE_PATH, year):
    """Precompute monthly and yearly totals for the given year."""
    try:
        # Check if the year is already precomputed
        if year in precomputed_totals:
            return precomputed_totals[year]

        sheet_name = f"date com {year}"
        df = pd.read_excel(FILE_PATH, sheet_name=sheet_name, header=2)

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df_year_filtered = df[df['Date'].dt.year == year]

        # Precompute monthly totals
        monthly_totals = df_year_filtered.groupby(df_year_filtered['Date'].dt.month)['Count of offense'].sum().to_dict()

        # Precompute the yearly total
        yearly_total = int(df_year_filtered['Count of offense'].sum())

        # Store in memoization dictionary
        precomputed_totals[year] = {"monthly_totals": monthly_totals, "yearly_total": yearly_total}
        return precomputed_totals[year]

    except Exception as e:
        print(f"Error in precompute_totals: {str(e)}")
        raise e

def generate_month_list(FILE_PATH, year, month):
    try:
        # Precompute totals for the year
        totals = precompute_totals(FILE_PATH, year)
        monthly_totals = totals["monthly_totals"]
        yearly_total = totals["yearly_total"]

        # Get the total offenses for the requested month
        month_total_offenses = int(monthly_totals.get(month, 0))

        # Calculate the percentage
        if yearly_total > 0:
            percentage = (month_total_offenses / yearly_total) * 100
        else:
            percentage = 0

        return {"totalAccidents": month_total_offenses, "percentage": round(percentage, 2)}

    except Exception as e:
        print(f"Error in generate_month_list: {str(e)}")
        raise e
