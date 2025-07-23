import pandas as pd

# Load the CSV
df = pd.read_csv('hmnist_28_28_RGB.csv')

# Shuffle the rows
df_shuffled = df.sample(frac=1).reset_index(drop=True)

# Save back to CSV (optional)
df_shuffled.to_csv('shuffled_file.csv', index=False)

# Show first few rows (optional)
print(df_shuffled.head())

