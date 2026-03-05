import os
import shutil
import random

# Update these to your actual paths
source_folder = "data"
subset_folder = "data_subset_300"
limit = 300

if not os.path.exists(subset_folder):
    os.makedirs(subset_folder)

# Get all images (handling potential case sensitivity in extensions)
images = [f for f in os.listdir(source_folder) if f.lower().endswith(('.tif', '.tiff', '.png'))]

# Shuffle and pick 300
random.shuffle(images)
selected = images[:limit]

for img_name in selected:
    shutil.copy(os.path.join(source_folder, img_name), os.path.join(subset_folder, img_name))

print(f"Success! {len(selected)} images moved to {subset_folder}")