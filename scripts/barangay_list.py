import pandas as pd

def generate_barangay_list(FILE_PATH):
    df_2022 = pd.read_excel(FILE_PATH, sheet_name='brgy 2022', header=2)
    df_2023 = pd.read_excel(FILE_PATH, sheet_name='brgy 2023', header=2)
    df_2024 = pd.read_excel(FILE_PATH, sheet_name='brgy 2024', header=2)
    
    df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)
    df = df.drop(['Count of barangay'], axis=1)

    # Filter out the "Grand Total" row
    df = df[df['Barangay Name'].str.lower() != 'grand total']

     # Filter out repeated barangay names
    df = df[~df['Barangay Name'].duplicated(keep='first')]

    return df['Barangay Name'].tolist()