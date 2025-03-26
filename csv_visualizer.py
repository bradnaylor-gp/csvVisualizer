import os
from datetime import datetime
from pathlib import Path

def wrapper(df, filePath, numeric_plots, categorical_plots, pairplot, heatmap):
    print("\n" + "+"*50)
    prompt2 = input("Export Generated Charts? y/n \n").strip()

    if prompt2.lower() != 'y':
        print("="*50)
        print("Exiting Script...")
        return

    # Create a directory name based on filepath and current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_stem = Path(filePath).stem
    output_dir = f"VisualizedData-{file_stem}-{current_date}"
    
    # Create the directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nCreated output directory: {output_dir}")
    except Exception as e:
        print(f"Error creating output directory: {e}")
        return

    # Create a dictionary mapping file names to chart types
    charts = {
        "numeric": os.path.join(output_dir, f"Numeric Chart_{file_stem}.png"),
        "categorical": os.path.join(output_dir, f"Categorical Chart_{file_stem}.png"),
        "pairplot": os.path.join(output_dir, f"Pairplot_{file_stem}.png"),
        "heatmap": os.path.join(output_dir, f"Correlation Heatmap_{file_stem}.png")
    }

    # Save the existing plots
    try:
        # Save numeric distribution plots
        if numeric_plots:
            numeric_plots.savefig(charts["numeric"], bbox_inches="tight")
            print(f"Saved numeric plots to: {charts['numeric']}")
        
        # Save categorical distribution plots
        if categorical_plots:
            categorical_plots.savefig(charts["categorical"], bbox_inches="tight")
            print(f"Saved categorical plots to: {charts['categorical']}")
        
        # Save pairplot if it exists
        if pairplot:
            pairplot.savefig(charts["pairplot"], bbox_inches="tight")
            print(f"Saved pairplot to: {charts['pairplot']}")
        
        # Save heatmap if it exists
        if heatmap:
            heatmap.savefig(charts["heatmap"], bbox_inches="tight")
            print(f"Saved heatmap to: {charts['heatmap']}")
        
        print("\nCharts exported successfully!")
    except Exception as e:
        print(f"Error exporting charts: {e}")

    print("\n" + "+"*50)