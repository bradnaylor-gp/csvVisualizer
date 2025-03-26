import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

def load_and_explore_data(file_path):
    """
    Load a CSV file and perform initial exploration
    """
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Display basic information
        print("="*50)
        print("File loaded successfully!")
        print(f"Shape: {df.shape} (rows, columns)")
        print("="*50)
        print("\nFirst 5 rows:")
        print(df.head())
        
        print("\n" + "="*50)
        print("\nData types and missing values:")
        print(df.info())
        
        print("\n" + "="*50)
        print("\nDescriptive statistics:")
        print(df.describe(include='all'))
        
        return df
    
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def visualize_data(df):
    """
    Create visualizations for the loaded data
    """
    if df is None:
        return
    
    # Set seaborn style
    sns.set_theme(style="whitegrid")
    
    # Create a figure with multiple plots
    plt.figure(figsize=(15, 10))
    
    # 1. Numeric distributions
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        print("\n" + "="*50)
        print("Creating visualizations for numeric columns...")
        
        # Plot distributions for numeric columns
        for i, col in enumerate(numeric_cols, 1):
            plt.subplot(2, 2, i)
            sns.histplot(data=df, x=col, kde=True)
            plt.title(f'Distribution of {col}')
            if i >= 4:  # Limit to 4 numeric plots for this example
                break
        
        plt.tight_layout()
        plt.show()
    
    # 2. Categorical distributions
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        print("\n" + "="*50)
        print("Creating visualizations for categorical columns...")
        
        plt.figure(figsize=(15, 5))
        for i, col in enumerate(categorical_cols, 1):
            plt.subplot(1, len(categorical_cols), i)
            sns.countplot(data=df, y=col, order=df[col].value_counts().index)
            plt.title(f'Distribution of {col}')
        plt.tight_layout()
        plt.show()
    
    # 3. Relationships between variables
    if len(numeric_cols) >= 2:
        print("\n" + "="*50)
        print("Creating relationship plots...")
        
        # Pairplot for numeric columns (first 5 to avoid overload)
        sns.pairplot(df[numeric_cols[:min(5, len(numeric_cols))]])
        plt.suptitle("Pairwise Relationships", y=1.02)
        plt.show()
        
        # Correlation heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
        plt.title("Correlation Heatmap")
        plt.show()
    
    # 4. Boxplots for numeric by categorical
    if len(numeric_cols) > 0 and len(categorical_cols) > 0:
        print("\n" + "="*50)
        print("Creating categorical-numeric relationship plots...")
        
        cat_col = categorical_cols[0]
        for num_col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            plt.figure(figsize=(10, 5))
            sns.boxplot(data=df, x=cat_col, y=num_col)
            plt.title(f'{num_col} by {cat_col}')
            plt.xticks(rotation=45)
            plt.show()

def main():
    # Ask for file path
    file_path = input("Enter the path to your CSV file: ").strip()
    
    # Verify file exists
    if not Path(file_path).exists():
        print("File not found. Please check the path and try again.")
        return
    
    # Load and explore data
    df = load_and_explore_data(file_path)
    
    # Visualize data
    visualize_data(df)

if __name__ == "__main__":
    print("CSV Data Visualization Tool")
    print("="*50)
    main()