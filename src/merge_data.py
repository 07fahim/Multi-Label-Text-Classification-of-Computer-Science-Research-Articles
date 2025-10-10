import pandas as pd

# List your CSV files
files = [
    "output\cs_2023_papers_10k.csv",
    "output\cs_2024_papers_10k.csv",
    "output\cs_2025_papers_10k.csv"
]

# Read and combine all CSVs
combined_df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


# Save the final combined file
output_file = "arxiv_cs_papers_combined.csv"
combined_df.to_csv(output_file, index=False)

print(f"Combined {len(files)} files successfully!")
print(f"Total unique records: {len(combined_df)}")
print(f"Saved as: {output_file}")
