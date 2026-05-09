import pandas as pd
import re

INPUT_FILE  = "Bill Wise party data.xls"
OUTPUT_FILE = "cleaned_data.csv"

print("Reading file...")
df_raw = pd.read_excel(INPUT_FILE, header=0, dtype=str)
df_raw.columns = [str(c).strip() for c in df_raw.columns]

party_pattern = re.compile(r"\[(\w+)\]\s*-\s*(.+)", re.IGNORECASE)

current_party_code = ""
current_party_name = ""
current_make       = ""
last_item          = ""

rows = []

for _, row in df_raw.iterrows():
    item = str(row.iloc[0]).strip()

    if not item or item == "nan":
        continue

    # Store header row
    m = party_pattern.match(item)
    if m:
        current_party_code = m.group(1).strip()
        current_party_name = m.group(2).strip()
        continue

    # Make row
    if item.lower().startswith("make"):
        current_make = item.split(":", 1)[-1].strip()
        continue

    # Column header row - skip
    if "description" in item.lower():
        continue

 # Skip total / footer rows
    skip_keywords = ["total", "grand tot", "rptparty", "subtotal"]
    if any(kw in item.lower() for kw in skip_keywords):
        continue

    # Skip rows where Amount is empty/nan
    amount_val = str(row.iloc[8]).strip()
    if not amount_val or amount_val == "nan":
        continue

    # Fill missing item description
    if item and item != "nan":
        last_item = item
    else:
        item = last_item

    # Clean date - remove time part
    date_val = str(row.iloc[2]).strip().replace(" 00:00:00", "").replace(" 00:00", "")
    try:
        date_val = pd.to_datetime(date_val, dayfirst=True).strftime("%d-%m-%Y")
    except:
        pass

    rows.append({
        "Party_Code"      : current_party_code,
        "Party_Name"      : current_party_name,
        "Item_Description": item,
        "Make"            : current_make,
        "Bill_No"         : str(row.iloc[1]).strip(),
        "Date"            : date_val,
        "Packing"         : str(row.iloc[3]).strip(),
        "Batch_No"        : str(row.iloc[4]).strip(),
        "Qty"             : str(row.iloc[5]).strip(),
        "Free"            : str(row.iloc[6]).strip(),
        "Rate"            : str(row.iloc[7]).strip(),
        "Amount"          : str(row.iloc[8]).strip(),
    })

df = pd.DataFrame(rows)

# Clean numeric columns
for col in ["Qty", "Free", "Rate", "Amount"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_csv(OUTPUT_FILE, index=False)

print(f"Done! Cleaned rows : {len(df)}")
print(f"Saved to           : {OUTPUT_FILE}")
print(df.to_string(index=False))