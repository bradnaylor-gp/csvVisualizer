import pandas as pd  # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
from pathlib import Path
from halo import Halo # type: ignore


def main():
    filePath = input("Please Enter File Path of CSV: ").strip()
    if not Path(filePath).exists():
        print("File not found. Check path and try again.")
        return
    try: 
        df = pd.read_csv(filePath)
        # Display basic information
        print("="*50)
        print("File loaded successfully!")
        print("\n" + "="*50)
        print("\nDescriptive statistics:")
        print(df.describe(include='all'))
        
        print("\n" + "="*50)
        print("\nData types and missing values:")
        print(df.info())
        
        
        print(f"Shape: {df.shape} (rows, columns)")
        print("="*50)
        print("\nFirst 5 rows:")
        print(df.head())
        print("\n" + "="*50)
        prompt1 = input("Visualize this Data? y/n \n").strip()
        if prompt1 != "y":
            print("="*50)
            print("Exiting Script...")
            return
        visualizeData(df, filePath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    
def visualizeData(df, filePath):
    numeric_plots = None
    categorical_plots = None
    pairplot = None
    heatmap = None

    #sns.set_theme(style="ticks")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        print("\n" + "="*50)
        print("Creating visualizations for numeric columns...")
        spinner = Halo(text='Data Visualizing...', spinner='dots')
        spinner.start()
        # Plot distributions for numeric columns
        plt.figure()  # Create a new figure
        for i, col in enumerate(numeric_cols, 1):
            plt.subplot(2, 2, i)
            sns.histplot(data=df, x=col, kde=True)
            plt.title(f'Distribution of {col}')
            if i >= 4:  # Limit to 4 numeric plots for this example
                break
        plt.tight_layout()
        numeric_plots = plt
        plt.show()
        spinner.stop()
        print("\n" + "="*50)
        print("Numeric Chart Generated...")
        print("\n" + "="*50)
        
    # 2. Categorical distributions
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        print("\n" + "="*50)
        print("Creating visualizations for categorical columns...")
        spinner = Halo(text='Data Visualizing...', spinner='dots')
        spinner.start()
        plt.figure(figsize=(15, 5))
        for i, col in enumerate(categorical_cols, 1):
            plt.subplot(1, len(categorical_cols), i)
            sns.countplot(data=df, y=col, order=df[col].value_counts().index)
            plt.title(f'Distribution of {col}')
        plt.tight_layout()
        categorical_plots = plt
        plt.show()
        spinner.stop()
        print("\n" + "="*50)
        print("Categorical Chart Generated...")
        print("\n" + "="*50)
        
    # 3. Relationships between variables
    if len(numeric_cols) >= 2:
        print("\n" + "="*50)
        print("Creating relationship plots...")
        spinner = Halo(text='Data Visualizing...', spinner='dots')
        spinner.start()
        # Pairplot for numeric columns (first 5 to avoid overload)
        pairplot = sns.pairplot(df[numeric_cols[:min(5, len(numeric_cols))]])
        plt.suptitle("Pairwise Relationships", y=1.02)
        plt.show()
        spinner.stop()

    # 4. Correlation heatmap
    if len(numeric_cols) >= 2:
        print("\n" + "="*50)
        print("Creating Correlation Heatmap...")
        spinner = Halo(text='Data Visualizing...', spinner='dots')
        spinner.start()
        plt.figure(figsize=(8, 6))
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
        plt.title("Correlation Heatmap")
        heatmap = plt
        plt.show()
        spinner.stop()
        print("\n" + "="*50)
        print("Categorical Chart Generated...")
        print("\n" + "="*50)
        
    wrapper(df, filePath, numeric_plots, categorical_plots, pairplot, heatmap)

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


if __name__ == "__main__":
    print("Simple CSV Data Visualization Tool")
    print("="*50)
    main()
