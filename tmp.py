# %%
import pandas as pd
import os

# Read Excel file without treating "NA" as missing values
df = pd.read_excel(os.path.join("input_data", "topological_task.xlsx"), keep_default_na=False)

# %%
# Shuffle the rows
df_shuffled = df.sample(frac=1).reset_index(drop=True)

# Save as CSV, preserving "NA" as string values
df_shuffled.to_csv("topological_task_shuffled.csv", index=False, na_rep="NA")
