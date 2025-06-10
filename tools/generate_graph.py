import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import numpy as np
import argparse
import os
import sys

def create_graph(test_folder, test_name):
    """
    Generates a request duration distribution graph from a CSV file
    found within the test_folder.
    """
    csv_file = os.path.join(test_folder, f"{test_name}.csv")
    output_file = os.path.join(test_folder, f"{test_name}.png")

    try:
        print(f"Generating graph from {csv_file}...")
        if not os.path.exists(csv_file):
            print(f"ERROR: CSV file not found: {csv_file}")
            return False

        # Load the CSV file
        df = pd.read_csv(csv_file)

        # Calculate percentiles
        data = df["duration_ms"]

        # 90. und 95. Perzentil berechnen
        p90 = data.quantile(0.90)
        p95 = data.quantile(0.95)

        # Plot
        plt.figure(figsize=(10, 6))
        sns.histplot(data, kde=True, stat="density", bins=30, color="skyblue", edgecolor="black")
        plt.axvline(p90, color='orange', linestyle='--', label=f'90. Perzentil ({p90:.2f} ms)')
        plt.axvline(p95, color='red', linestyle='--', label=f'95. Perzentil ({p95:.2f} ms)')

        # Optionale: echte Normalverteilung
        mean = data.mean()
        std = data.std()
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mean, std)
        plt.plot(x, p, "k", linewidth=1.5, label="Normalverteilung")

        # Beschriftung
        plt.title(f"Request Duration Distribution for {test_name}")
        plt.xlabel("Request Dauer ( ms)")
        plt.ylabel("Dichte")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(output_file)
        plt.close()
        print(f"Graph saved to {output_file}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to generate graph for {test_name}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a request duration distribution graph from a CSV file.")
    parser.add_argument("--test-folder", required=True, help="Path to the folder containing the test's CSV file.")
    parser.add_argument("--test-name", required=True, help="Name of the test (e.g., 'docker_request').")
    args = parser.parse_args()
    
    create_graph(args.test_folder, args.test_name)