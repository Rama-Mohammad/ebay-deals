import pandas as pd

# Load raw CSV with all columns as strings
df = pd.read_csv("ebay_tech_deals.csv", dtype=str)

# Clean price and original_price
for col in ["price", "original_price"]:
    df[col] = df[col].str.replace("US \$", "", regex=True)
    df[col] = df[col].str.replace(",", "", regex=True)
    df[col] = df[col].str.strip()

# Replace missing original_price with price
df["original_price"] = df["original_price"].replace({"N/A": "", None: ""})
df["original_price"] = df["original_price"].mask(df["original_price"] == "", df["price"])

# Clean shipping
df["shipping"] = df["shipping"].replace({"N/A": "", None: ""})
df["shipping"] = df["shipping"].apply(lambda x: x.strip() if pd.notna(x) else "")
df["shipping"] = df["shipping"].replace({"": "Shipping info unavailable"})

# Convert to numeric
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")

# Compute discount_percentage using the formula she wants
df["discount_percentage"] = ((1 - df["price"] / df["original_price"]) * 100).round(2)
df["discount_percentage"] = df["discount_percentage"].fillna(0)

# Remove duplicates based on item_url
df = df.drop_duplicates(subset=["item_url"], keep="last")

# Save cleaned CSV
df.to_csv("cleaned_ebay_deals.csv", index=False)

print(f"Cleaned data saved: {len(df)} rows (duplicates removed).")