import os
import subprocess
import shutil
from processor import run_analysis_pipeline

def main():
    print("Starting Foci Analysis Pipeline")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Run the Python Processor
    # Looking for 'data' in the project root
    input_folder = os.path.join(BASE_DIR, '..', 'data')
    # Saving CSV to the 'results' folder
    output_csv = os.path.join(BASE_DIR, '..', 'results', 'foci_counts.csv')

    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found!")
        return

    print(f"\n[1/2] Processing images in '{input_folder}'...")
    df_results = run_analysis_pipeline(input_folder, output_csv)
    print(f"Success: {len(df_results)} images processed.")

    # Run the R Statistical Validation
    print("\n[2/2] Running R Statistical Validation...")
    try:
        r_cmd = "Rscript"

        if not shutil.which(r_cmd):
            r_cmd = r"C:\Program Files\R\R-4.4.1\bin\Rscript.exe"

        # Point directly to analysis.R in the scripts folder
        r_script_path = os.path.join(BASE_DIR, "analysis.R")

        subprocess.run([r_cmd, r_script_path], check=True)
        print("Success: Validation plot generated in 'results' folder.")

    except Exception as e:
        print(f"R Analysis failed. Error: {e}")


if __name__ == "__main__":
    main()