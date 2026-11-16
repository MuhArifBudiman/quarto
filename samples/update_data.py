
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "dataset" / "credit_card_fraud_detection_2026.csv"


def main(new_data=None):

    # Read existing dataset
    df = pd.read_csv(DATASET_PATH)

    # Return original dataset if no new data
    if new_data is None:
        return df

    # Combine existing and new data
    df_final = pd.concat(
        [df, new_data],
        ignore_index=True
    )

    df_final.to_csv("samples/updated_data.csv")
    return print("Saved")


if __name__ == "__main__":

    sample_data = pd.read_csv(DATASET_PATH).sample(5)

    main(new_data=sample_data)
