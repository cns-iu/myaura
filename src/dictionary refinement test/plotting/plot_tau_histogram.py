import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('../results/csv/thR_8_1000_tau.csv', index_col=False)

# Plotting histograms for each field in the table
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 10))
fig.suptitle('Histograms for Each Field', fontsize=16)

# Flatten the axes array for easy iteration
axes = axes.flatten()

for i, column in enumerate(data.columns):
    axes[i].hist(data[column], bins=20, color='skyblue', edgecolor='black')
    axes[i].set_title(column)

# Adjust layout to prevent overlap
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Show the plots
plt.savefig('../results/plot/thR_8_1000_tau_hist.png')