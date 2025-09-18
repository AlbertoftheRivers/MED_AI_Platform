import os
import shutil
import pandas as pd
import re

# Get the project root (where this script's parent is)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Paths
base_dir = os.path.join(project_root, "data", "chest_xray")
output_dir = os.path.join(project_root, "data")
csv_path = os.path.join(output_dir, "labels.csv")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Debug: Print paths to verify
print(f"Looking for images in: {base_dir}")
print(f"Output directory: {output_dir}")

# Prepare CSV data
csv_rows = []

# Helper to parse filename - more flexible version
def parse_filename(filename):
    # Try multiple patterns
    patterns = [
        r"(VIRUS|BACTERIA|NORMAL)[_\-]?(.+)[_\-]?(\d+)\.jpeg"]
    
    filename_upper = filename.upper()
    for pattern in patterns:
        match = re.match(pattern, filename_upper, re.IGNORECASE)
        if match:
            groups = match.groups()
            if "VIRUS" in groups:
                kind = "VIRUS"
            elif "BACTERIA" in groups:
                kind = "BACTERIA"
            elif "NORMAL" in groups:
                kind = "NORMAL"
            else:
                continue
                
            # Get patient and image number from remaining groups
            other_groups = [g for g in groups if g.upper() not in ["VIRUS", "BACTERIA", "NORMAL"]]
            if len(other_groups) >= 2:
                patient, img_num = other_groups[0], other_groups[1]
            elif len(other_groups) == 1:
                patient, img_num = other_groups[0], "1"  # default image number
            else:
                patient, img_num = "unknown", "1"
            
            if kind == "VIRUS":
                outcome = "P_VIRUS"
            elif kind == "BACTERIA":
                outcome = "P_BAC"
            else:
                outcome = "NORMAL"
            
            return patient, img_num, outcome
    
    return None

# Walk through train and test folders
found_images = 0
for split in ["train", "test"]:
    for label in ["PNEUMONIA", "NORMAL"]:
        folder = os.path.join(base_dir, split, label)
        if not os.path.exists(folder):
            print(f"⚠️ Folder not found: {folder}")
            continue
            
        print(f"Processing folder: {folder}")
        for fname in os.listdir(folder):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
                
            print(f"Found image: {fname}")
            parsed = parse_filename(fname)
            if not parsed:
                print(f"⚠️ Could not parse filename: {fname}")
                continue
                
            patient, img_num, outcome = parsed
            src = os.path.join(folder, fname)
            dst = os.path.join(output_dir, fname)
            
            # If duplicate name, add split to filename
            if os.path.exists(dst):
                base, ext = os.path.splitext(fname)
                dst = os.path.join(output_dir, f"{base}_{split}{ext}")
                
            shutil.copy2(src, dst)
            csv_rows.append({
                "patient": patient,
                "image_number": img_num,
                "outcome": outcome,
                "filename": os.path.basename(dst)
            })
            found_images += 1
            print(f"Processed: {fname} -> {outcome}")

if found_images == 0:
    print("⚠️ No images found. Please check:")
    print(f"1. The directory structure at: {base_dir}")
    print("2. The filename patterns (current parser expects something like 'VIRUS_patient_123.png')")
    print("3. File extensions (looking for .png, .jpg, .jpeg)")

# Save CSV if we found any images
if csv_rows:
    df = pd.DataFrame(csv_rows)
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV saved at {csv_path} with {len(df)} rows.")
else:
    print("⏹️ No CSV created - no valid images found")
