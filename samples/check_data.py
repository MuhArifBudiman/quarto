from update_data import main
import os
import pandas as pd
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


DATASET_PATH = ROOT_DIR / "dataset" / "credit_card_fraud_detection_2026.csv"


def main_check():

    if os.path.exists("updated_data.csv"):
        df = pd.read_csv("updated_data.csv")
    else:
        df = pd.read_csv(DATASET_PATH)
    return df
