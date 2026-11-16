import shutil
import subprocess
from pathlib import Path

import pandas as pd

DATA = "dataset/credit_card_fraud_detection_2026.csv"
QMD = Path("demo_format_parameterize.qmd")
FORMAT = "pptx"  # html, pptx, docx
LIMIT = 10        # uji 2 negara dulu; ganti None untuk semua
OUT_DIR = Path("_output/report_generator").resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    quarto = shutil.which("quarto")  # path lengkap, aman di Windows
    countries = (
        pd.read_csv(DATA, usecols=["merchant_country"])["merchant_country"]
        .dropna()
        .unique()
    )

    for c in countries[:LIMIT]:
        safe = str(c).replace(" ", "_").replace("/", "-")
        out = f"report_{safe}.{FORMAT}"
        print(f"Render: {c} -> {out}")

        subprocess.run(
            [quarto, "render", str(QMD), "--to", FORMAT,
             "-P", f"country:{c}", "--output", out],
            check=True,
        )

        # Quarto menaruh hasil di sebelah .qmd; pindahkan ke folder tujuan
        produced = Path(out)
        if not produced.exists():
            raise FileNotFoundError(f"Hasil tidak ditemukan di: {produced}")
        produced.replace(OUT_DIR / out)
        print(f"  -> {OUT_DIR / out}")


if __name__ == "__main__":
    main()
