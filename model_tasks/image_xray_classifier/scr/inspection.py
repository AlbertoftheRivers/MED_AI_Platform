import pandas as pd

# Define the path to the CSV file
csv_path = (
    "c:/Users/beto1/.cache/data_extracted/data/Data_Entry_2017.csv"
)

# Read the CSV file
df = pd.read_csv(csv_path)

# Split the 'Finding Labels' by '|' and get unique classes
all_labels = set()
df['Finding Labels'].str.split('|').apply(all_labels.update)

# Print the number of different classes
print(f"Number of different classes: {len(all_labels)}")
print("Classes:", all_labels)