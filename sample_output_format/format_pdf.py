# %% [markdown]
# ---
# title: "Report EDA Fraud"
# format:
#   typst: default
# execute:
#   echo: false
#   warning: false
# ---

# %%
# | echo: false
from matplotlib.ticker import PercentFormatter
import os
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from IPython.display import Markdown, display

sns.set_theme(style="whitegrid")

DIR_FILE = Path.cwd()
ROOT_DIR = os.path.dirname(DIR_FILE)
DATASET_PATH = os.path.join(
    ROOT_DIR, "dataset", "credit_card_fraud_detection_2026.csv"
)
df = pd.read_csv(DATASET_PATH)

n_total = len(df)
n_fraud = int(df["is_fraud"].sum())
baseline = n_fraud / n_total

# %% [markdown]
# # Data Analysis Report
#
# ## 1. Introduction
#
# Laporan EDA demo untuk mengidentifikasi sinyal yang membedakan transaksi
# fraud dari non-fraud pada dataset kartu kredit.
#
# ## 2. Dataset Overview
#
# ### 2.1 Struktur Data

# %%
# | echo: false
display(Markdown(
    f"Dataset berisi **{n_total:,}** transaksi dan **{df.shape[1]}** kolom."
))
df.info()

# %% [markdown]
# ### 2.2 Ringkasan Numerik

# %%
# | echo: false
num_cols = ["transaction_amount", "customer_age", "account_age_days",
            "credit_limit", "credit_score"]
df[num_cols].describe().T.round(2)

# %% [markdown]
# ### 2.3 Missing Value & Cek Konsistensi

# %%
# | echo: false
miss = df.isna().sum()
miss = miss[miss > 0].rename("n_missing").to_frame()
miss["pct"] = (miss["n_missing"] / n_total * 100).round(2)
display(miss)

checks = pd.DataFrame({
    "cek": [
        "browser kosong == channel In-store/ATM",
        "fraud_type != Legitimate == is_fraud",
    ],
    "lolos": [
        bool((df["browser"].isna() ==
              df["transaction_channel"].isin(["In-store", "ATM"])).all()),
        bool(((df["fraud_type"] != "Legitimate").astype(int)
              == df["is_fraud"]).all()),
    ],
})
display(checks)

# %% [markdown]
# Kolom `browser` kosong secara struktural (transaksi non-online), jadi tidak
# di-impute.

# %% [markdown]
# ### 2.4 Distribusi Fraud

# %%
# | echo: false
counts = (df["is_fraud"].map({0: "Non-fraud", 1: "Fraud"})
          .value_counts().reindex(["Non-fraud", "Fraud"]))

fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(x=counts.index, y=counts.values, ax=ax)
for i, v in enumerate(counts.values):
    ax.text(i, v, f"{v:,}", ha="center", va="bottom")
ax.set_title("Fraud Distribution")
ax.set_xlabel("Transaction Class")
ax.set_ylabel("Number of Transactions")
plt.tight_layout()
plt.show()

display(Markdown(
    f"- Fraud: **{n_fraud:,}** dari {n_total:,} transaksi "
    f"(**{baseline:.2%}**).\n"
    f"- Data sangat imbalanced; angka {baseline:.2%} dipakai sebagai "
    f"baseline di analisis berikutnya."
))

# %% [markdown]
# ## 3. Exploratory Data Analysis
#
# ### 3.1 Nilai Transaksi: Fraud vs Non-fraud

# %%
# | echo: false
plot_df = df.assign(
    kelas=df["is_fraud"].map({0: "Non-fraud", 1: "Fraud"})
)

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=plot_df, x="kelas", y="transaction_amount",
            order=["Non-fraud", "Fraud"], log_scale=True, ax=ax)
ax.set_title("Transaction Amount by Class (log scale)")
ax.set_xlabel("Transaction Class")
ax.set_ylabel("Transaction Amount ($, log)")
plt.tight_layout()
plt.show()

med = df.groupby("is_fraud")["transaction_amount"].median()
display(Markdown(
    f"- Median nilai transaksi: non-fraud **\\${med[0]:,.2f}**, "
    f"fraud **\\${med[1]:,.2f}** "
    f"(rasio {med[1] / med[0]:.1f}x)."
))

# %% [markdown]
# ### 3.2 Fraud Amount Analysis

# %%
# | echo: false
fraud_data = df.loc[df["is_fraud"] == 1].copy()

median_loss = fraud_data["fraud_amount_lost"].median()
mean_loss = fraud_data["fraud_amount_lost"].mean()
max_loss = fraud_data["fraud_amount_lost"].max()
total_loss = fraud_data["fraud_amount_lost"].sum()

# puncak histogram menggantikan mode() (data kontinu)
hist_vals, edges = np.histogram(fraud_data["fraud_amount_lost"], bins=40)
peak = (edges[hist_vals.argmax()] + edges[hist_vals.argmax() + 1]) / 2

fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(data=fraud_data, x="fraud_amount_lost", bins=40,
             kde=True, ax=ax)
ax.axvline(peak, linestyle="--", linewidth=2,
           label=f"Peak: ${peak:,.2f}")
ax.axvline(median_loss, linestyle="-.", linewidth=2, color="red",
           label=f"Median: ${median_loss:,.2f}")
ax.set_title("Distribution of Fraud Amount Lost")
ax.set_xlabel("Fraud Amount Lost ($)")
ax.set_ylabel("Frequency")
ax.legend()
plt.tight_layout()
plt.show()

display(Markdown(
    f"- Total kerugian: **\\${total_loss:,.0f}**; "
    f"rata-rata \\${mean_loss:,.2f}, median \\${median_loss:,.2f}.\n"
    f"- Kerugian terbesar: **\\${max_loss:,.2f}**; "
    f"puncak distribusi di sekitar \\${peak:,.0f}.\n"
    f"- Rata-rata > median menandakan distribusi miring ke kanan."
))
# %%
# | echo: false


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h


def rate_table(data, col, min_n=500):
    g = (data.groupby(col)
         .agg(n=("is_fraud", "size"), fraud=("is_fraud", "sum"))
         .reset_index())
    g = g[g["n"] >= min_n].copy()  # segmen < min_n tidak diranking
    g["rate"] = g["fraud"] / g["n"]
    g["lift"] = g["rate"] / baseline
    g["lo"], g["hi"] = wilson(g["fraud"], g["n"])
    return g


def plot_rate(g, col, title, order=None, figsize=(8, 5), fs=10):
    if order is not None:
        g = g.set_index(col).loc[order].reset_index()
    else:
        g = g.sort_values("rate", ascending=False)
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=g, y=col, x="rate", order=g[col].tolist(),
                color="C0", ax=ax)
    ax.errorbar(g["rate"].values, np.arange(len(g)),
                xerr=[(g["rate"] - g["lo"]).values,
                      (g["hi"] - g["rate"]).values],
                fmt="none", ecolor="black", capsize=2, lw=1)
    ax.axvline(baseline, ls="--", color="red",
               label=f"Baseline {baseline:.2%}")
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=1))
    ax.tick_params(axis="y", labelsize=fs)
    ax.set_title(title)
    ax.set_xlabel("Fraud Rate (95% CI)")
    ax.set_ylabel("")
    ax.legend()
    plt.tight_layout()
    plt.show()


def summarize(g, col):
    s = g.sort_values("rate")
    top, low = s.iloc[-1], s.iloc[0]
    n_sig = int((g["lo"] > baseline).sum())
    display(Markdown(
        f"- Tertinggi: **{top[col]}** {top['rate']:.2%} "
        f"(lift {top['lift']:.2f}x; {int(top['fraud'])} fraud dari "
        f"{int(top['n']):,}).\n"
        f"- Terendah: **{low[col]}** {low['rate']:.2%} "
        f"(lift {low['lift']:.2f}x).\n"
        f"- {n_sig} dari {len(g)} segmen punya batas bawah CI di atas "
        f"baseline."
    ))

# %% [markdown]
# ### 3.3 Temporal
#
# #### 3.3.1 Fraud Rate per Jam


# %%
# | echo: false
g = rate_table(df, "transaction_hour")

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(g["transaction_hour"], g["rate"], marker="o", color="C0")
ax.fill_between(g["transaction_hour"], g["lo"], g["hi"], alpha=0.2)
ax.axhline(baseline, ls="--", color="red",
           label=f"Baseline {baseline:.2%}")
ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=1))
ax.set_xticks(range(0, 24, 2))
ax.set_title("Fraud Rate by Hour of Day")
ax.set_xlabel("Hour")
ax.set_ylabel("Fraud Rate (95% CI)")
ax.legend()
plt.tight_layout()
plt.show()

top3 = g.nlargest(3, "rate")
display(Markdown(
    "- Jam tertinggi: " + ", ".join(
        f"**{int(h):02d}:00** ({r:.2%})"
        for h, r in zip(top3["transaction_hour"], top3["rate"])) + ".\n"
    f"- {int((g['lo'] > baseline).sum())} dari 24 jam punya batas bawah "
    f"CI di atas baseline."
))

# %% [markdown]
# #### 3.3.2 Fraud Rate per Hari

# %%
# | echo: false
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday"]
g = rate_table(df, "transaction_day_of_week")
plot_rate(g, "transaction_day_of_week", "Fraud Rate by Day of Week",
          order=days, figsize=(8, 4))
summarize(g, "transaction_day_of_week")

# %% [markdown]
# ### 3.4 Kategorikal
#
# Pembanding semua plot adalah baseline fraud rate keseluruhan (garis
# merah). Lift = rate segmen / baseline. Segmen < 500 transaksi tidak
# diranking.
#
# #### 3.4.1 Negara Merchant

# %%
# | echo: false
g = rate_table(df, "merchant_country")
plot_rate(g, "merchant_country", "Fraud Rate by Merchant Country",
          figsize=(8, 7))
summarize(g, "merchant_country")

share = (g.assign(share_fraud=g["fraud"] / g["fraud"].sum(),
                  share_volume=g["n"] / g["n"].sum())
         .nlargest(5, "share_fraud")
         [["merchant_country", "n", "fraud", "share_fraud",
           "share_volume"]]
         .round(4))
display(share)

# %% [markdown]
# Tabel di atas: 5 negara penyumbang fraud terbanyak, dibandingkan share
# fraud vs share volume transaksinya.

# %% [markdown]
# #### 3.4.2 Kategori Merchant

# %%
# | echo: false
g = rate_table(df, "merchant_category")
plot_rate(g, "merchant_category", "Fraud Rate by Merchant Category",
          figsize=(8, 6))
summarize(g, "merchant_category")

# %% [markdown]
# #### 3.4.3 Channel dan Browser

# %%
# | echo: false
g = rate_table(df, "transaction_channel")
plot_rate(g, "transaction_channel", "Fraud Rate by Channel",
          figsize=(8, 3.5))
summarize(g, "transaction_channel")

# %%
# | echo: false
g = rate_table(df[df["transaction_channel"] == "Online"], "browser")
plot_rate(g, "browser", "Fraud Rate by Browser (Online channel only)",
          figsize=(8, 3.5))
summarize(g, "browser")

# %% [markdown]
# #### 3.4.4 Email Domain dan Gender

# %%
# | echo: false
g = rate_table(df, "email_domain")
plot_rate(g, "email_domain", "Fraud Rate by Email Domain",
          figsize=(8, 3.5))
summarize(g, "email_domain")

# %%
# | echo: false
display(Markdown("Gender: deskriptif saja, tidak dijadikan kandidat aturan."))
display(rate_table(df, "customer_gender", min_n=0)
        [["customer_gender", "n", "fraud", "rate", "lift"]].round(4))

# %% [markdown]
# #### 3.4.5 Jenis Fraud

# %%
# | echo: false
fd = df[df["is_fraud"] == 1]
ft = (fd.groupby("fraud_type")["fraud_amount_lost"]
      .agg(n="size", total="sum", mean="mean", median="median")
      .sort_values("total", ascending=False))
ft["share_n"] = ft["n"] / ft["n"].sum()
ft["share_loss"] = ft["total"] / ft["total"].sum()
display(ft.round(2))

fig, ax = plt.subplots(figsize=(8, 4))
ft[["share_n", "share_loss"]].plot.barh(ax=ax)
ax.invert_yaxis()
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_title("Share of Fraud Cases vs Share of Loss by Fraud Type")
ax.set_xlabel("Share")
ax.set_ylabel("")
ax.legend(["Share of cases", "Share of loss"])
plt.tight_layout()
plt.show()

top_loss = ft.index[0]
display(Markdown(
    f"- Penyumbang kerugian terbesar: **{top_loss}** "
    f"({ft.loc[top_loss, 'share_loss']:.1%} dari total kerugian, "
    f"{ft.loc[top_loss, 'share_n']:.1%} dari jumlah kasus)."
))

# %% [markdown]
# #### 3.4.6 Lampiran: State Pelanggan

# %%
# | echo: false
g = rate_table(df, "customer_state")
plot_rate(g, "customer_state", "Fraud Rate by Customer State",
          figsize=(8, 10), fs=7)
summarize(g, "customer_state")
