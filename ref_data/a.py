# import ast
# import pandas as pd

# with open('backend/ref_data/session_info.json', 'r') as f:
#     data = ast.literal_eval(f.read())  # Handles Python dict syntax

# # Convert to DataFrame
# df = pd.DataFrame([v for v in data.values() if isinstance(v, dict)])
# print(df.head())

import ast
import pandas as pd
import csv

# 1. Load and parse the data
with open('backend/ref_data/session_info.json', 'r') as f:
    session_data = ast.literal_eval(f.read())

# 2. Convert to DataFrame
session_df = pd.DataFrame([session_data])

# 3. Save to CSV
csv_path = 'backend/ref_data/session_info_verified.csv'
session_df.to_csv(csv_path, 
                 index=False,
                 na_rep='null',  # Represent None/null values explicitly
                 quoting=csv.QUOTE_NONNUMERIC,  # Proper quoting for text
                 )

# 4. Display verification info
print(f"Data successfully saved to: {csv_path}")
print(f"\nShape: {session_df.shape} (rows x columns)")
print("\nFirst 3 rows:")
print(session_df.head(3).to_string(index=False))

print("\nColumn names:")
print("\n".join(session_df.columns.tolist()))
# import json
# import pandas as pd

# def load_and_convert_json(filepath):
#     try:
#         # Read the file content first
#         with open(filepath, 'r') as f:
#             content = f.read()
        
#         # Check if the content needs cleaning
#         if not content.strip().startswith('{'):
#             # Try to fix common JSON formatting issues
#             content = content.replace("'", '"')  # Replace single quotes with double
#             content = content.replace("None", "null")  # Replace Python None with JSON null
#             content = content.replace("True", "true")  # Replace Python True with JSON true
#             content = content.replace("False", "false") # Replace Python False with JSON false
        
#         # Parse the JSON
#         data = json.loads(content)
        
#         # Extract drivers (ignore metadata)
#         drivers = {k: v for k, v in data.items() 
#                   if isinstance(v, dict) and 'RacingNumber' in v}
        
#         # Convert to DataFrame
#         df = pd.DataFrame.from_dict(drivers, orient='index')
        
#         # Clean and enhance the data
#         if 'TeamColour' in df.columns:
#             df['TeamColor'] = '#' + df['TeamColour'].astype(str)
        
#         # Reorder columns logically
#         col_order = ['RacingNumber', 'FullName', 'BroadcastName', 'FirstName', 
#                     'LastName', 'Tla', 'TeamName', 'TeamColor', 'Line', 
#                     'Reference', 'HeadshotUrl']
#         df = df[[c for c in col_order if c in df.columns]]
        
#         return df
    
#     except Exception as e:
#         print(f"Error processing file: {e}")
#         return None

# # Usage
# file_path = 'backend/ref_data/driver_list.json'
# driver_df = load_and_convert_json(file_path)

# if driver_df is not None:
#     print("Successfully loaded driver data:")
#     print(driver_df.head())
    
#     # Save to CSV if needed
#     driver_df.to_csv('f1_drivers_clean.csv', index=False)
#     print("\nData saved to 'f1_drivers_clean.csv'")
# else:
#     print("Failed to load driver data")