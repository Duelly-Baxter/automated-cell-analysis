import os
import numpy as np
import pandas as pd
import warnings
from tqdm import tqdm
from skimage import io, filters, morphology
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
import matplotlib.pyplot as plt


def generate_report_figure(image_path):
    """
    Generates a high-quality side-by-side comparison for the technical supplement.
    """
    # Use your existing logic to get the labels
    raw_image = io.imread(image_path, as_gray=True)
    denoised = filters.gaussian(raw_image, sigma=1)
    thresh = filters.threshold_otsu(denoised)
    binary = denoised > thresh
    cleaned = morphology.remove_small_objects(binary, min_size=25)
    distance = ndi.distance_transform_edt(cleaned)
    coords = peak_local_max(distance, min_distance=3, labels=cleaned)

    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = ndi.label(mask)
    labels = watershed(-distance, markers, mask=cleaned)

    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    ax1.imshow(raw_image, cmap='gray')
    ax1.set_title("Microscopy (Channel W2)", fontsize=14)
    ax1.axis('off')

    # Color each nucleus differently to show individual segmentation
    ax2.imshow(labels, cmap='nipy_spectral')
    ax2.set_title(f"Watershed Results: {len(np.unique(labels)) - 1} Cell(s) Detected", fontsize=14)
    ax2.axis('off')

    plt.tight_layout()
    plt.savefig("validation_figure.png", dpi=300)
    print("\n[SUCCESS] Report figure saved as 'validation_figure.png'")
    plt.show()

# Setup & Configuration
warnings.filterwarnings("ignore")


def process_single_image(path):
    """
    Uses Watershed segmentation to separate touching foci and return accurate counts.
    """
    raw_image = io.imread(path, as_gray=True)

    # Subtle Denoising
    denoised = filters.gaussian(raw_image, sigma=1)

    # Thresholding
    thresh = filters.threshold_otsu(denoised)
    binary = denoised > thresh

    # Cleanup: Remove small noise specks
    cleaned = morphology.remove_small_objects(binary, min_size=25)

    # Watershed Segmentation
    # Calculate the distance transform: how far each white pixel is from the black background
    distance = ndi.distance_transform_edt(cleaned)

    # Find the local peaks (centers of the foci)
    # min_distance=3 prevents over-splitting a single bumpy focus
    coords = peak_local_max(distance, min_distance=3, labels=cleaned)

    # Create marker seeds for the watershed from these peaks
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = ndi.label(mask)

    # The actual watershed: 'floods' from markers until they hit the boundary of the 'cleaned' mask
    labels = watershed(-distance, markers, mask=cleaned)

    # Count unique objects (excluding background 0)
    unique_labels = np.unique(labels)
    count = len(unique_labels[unique_labels > 0])

    return count


def parse_metadata(filename):
    """Extracts the 'C' ground truth from the filename."""
    parts = filename.split('_')
    try:
        cells_part = [p for p in parts if p.startswith('C')][0]
        return int(cells_part.replace('C', ''))
    except (IndexError, ValueError):
        return 0


def run_analysis_pipeline(input_dir, output_file):
    """The Manager function with built-in resume Logic."""
    all_files = [f for f in os.listdir(input_dir)
                 if f.lower().endswith(('.tif', '.tiff')) and 'w2' in f.lower()]

    results = []
    processed_files = set()

    if os.path.exists(output_file):
        try:
            existing_df = pd.read_csv(output_file)
            results = existing_df.to_dict('records')
            processed_files = set(existing_df['filename'].astype(str).tolist())
            print(f"Found existing progress. Skipping {len(processed_files)} images.")
        except Exception as e:
            print(f"Could not read existing CSV ({e}). Starting fresh.")

    remaining_files = [f for f in all_files if f not in processed_files]

    if not remaining_files:
        print("All images already processed!")
        return pd.DataFrame(results)

    for i, filename in enumerate(tqdm(remaining_files, desc="Processing Foci", unit="img")):
        path = os.path.join(input_dir, filename)
        try:
            detected = process_single_image(path)
            actual = parse_metadata(filename)

            results.append({
                'filename': filename,
                'detected': detected,
                'actual': actual,
                'error': detected - actual
            })

            if (i + 1) % 500 == 0:
                pd.DataFrame(results).to_csv(output_file, index=False)

        except Exception as e:
            print(f"\n Error on {filename}: {e}")
            continue

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    return df


if __name__ == "__main__":
    final_df = run_analysis_pipeline(input_dir='data', output_file='foci_counts.csv')
    print(f"\nProcessed {len(final_df)} images successfully.")