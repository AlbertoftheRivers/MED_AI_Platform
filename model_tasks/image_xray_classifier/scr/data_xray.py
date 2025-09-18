import os
import pandas as pd
import shutil
import zipfile

# === Paths ===
extract_dir = r"C:\Users\beto1\.cache\data_extracted"
images_root = os.path.join(extract_dir, "data")
csv_path = os.path.join(images_root, "Data_Entry_2017.csv")
output_dir = os.path.join(r"C:\Users\beto1\.cache", "data_div")
output_data_dir = os.path.join(output_dir, "data")
os.makedirs(output_data_dir, exist_ok=True)

# === Step 1: Load and reduce CSV ===
df = pd.read_csv(csv_path)
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
df_half = df_shuffled.iloc[:len(df)//2]
selected_images = set(df_half["Image Index"])

# === Step 2: Copy selected images while preserving folder structure ===
for i in range(1, 13):
    src_subfolder = f"images_{i:03d}/images"
    src_folder_path = os.path.join(images_root, src_subfolder)
    
    if not os.path.exists(src_folder_path):
        continue

    dst_images_path = os.path.join(output_data_dir, f"images_{i:03d}", "images")
    os.makedirs(dst_images_path, exist_ok=True)

    for img_name in os.listdir(src_folder_path):
        if img_name in selected_images:
            src_path = os.path.join(src_folder_path, img_name)
            dst_path = os.path.join(dst_images_path, img_name)
            shutil.copy2(src_path, dst_path)

# === Step 3: Save reduced CSV ===
csv_output_path = os.path.join(output_data_dir, "Data_Entry_2017.csv")
df_half.to_csv(csv_output_path, index=False)

num_images_copied = 0
for i in range(1, 13):
    dst_images_path = os.path.join(output_data_dir, f"images_{i:03d}", "images")
    if os.path.exists(dst_images_path):
        num_images_copied += len(os.listdir(dst_images_path))
print(f"Total images copied: {num_images_copied}")
print(f"CSV entries kept: {len(df_half)}")


# === Step 4: Zip the folder ===
zip_output = os.path.join(r"C:\Users\beto1\.cache", "data_div.zip")
with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, output_dir)
            zipf.write(full_path, arcname=rel_path)

print("✅ Reduced zip created at:", zip_output)
