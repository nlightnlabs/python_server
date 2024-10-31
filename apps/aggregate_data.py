import pandas as pd

# Sample data
data = [
    {'id': 1, 'category': 'A', 'spend': 1000},
    {'id': 2, 'category': 'B', 'spend': 500},
    {'id': 3, 'category': 'A', 'spend': 750},
    {'id': 4, 'category': 'C', 'spend': 200},
    {'id': 5, 'category': 'A', 'spend': 434},
    {'id': 6, 'category': 'B', 'spend': 732},
    {'id': 7, 'category': 'A', 'spend': 820},
    {'id': 8, 'category': 'C', 'spend': 123},
    {'id': 9, 'category': 'A', 'spend': 3023},
    {'id': 10, 'category': 'D', 'spend': 343}
]

# Create a DataFrame
df = pd.DataFrame(data)

# Group by 'category' and aggregate 'spend' with multiple functions
aggregated_df = df.groupby('category')['spend'].agg(
    sum_spend='sum',
    avg_spend='mean',
    median_spend='median',
    min_spend='min',
    max_spend='max'
).reset_index()

# Display the result
print(aggregated_df)