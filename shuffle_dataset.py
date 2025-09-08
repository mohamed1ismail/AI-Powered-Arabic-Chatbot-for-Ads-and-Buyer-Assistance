#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# --- Configuration ---
CSV_PATH = 'dataset/ads_dataset.csv'

def shuffle_dataset():
    """Reads, shuffles, and overwrites the ads dataset CSV."""
    print(f"Reading dataset from {CSV_PATH}...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(CSV_PATH)
        
        # Shuffle the DataFrame
        print("Shuffling dataset...")
        df_shuffled = df.sample(frac=1).reset_index(drop=True)
        
        # Save the shuffled DataFrame back to the CSV
        df_shuffled.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
        
        print(f"Successfully shuffled and saved the dataset to {CSV_PATH}.")
        print(f"Total rows: {len(df_shuffled)}")

    except FileNotFoundError:
        print(f"Error: The file {CSV_PATH} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    shuffle_dataset()
