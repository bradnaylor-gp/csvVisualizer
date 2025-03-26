import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_rows=100):
    """Generate a sample dataset with multiple data types"""
    np.random.seed(42)
    
    # Generate dates
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(num_rows)]
    
    # Generate categories
    categories = np.random.choice(['Electronics', 'Clothing', 'Home', 'Books', 'Sports'], size=num_rows)
    regions = np.random.choice(['North', 'South', 'East', 'West'], size=num_rows, p=[0.3, 0.2, 0.4, 0.1])
    
    # Generate numerical data with some relationships
    sales = np.random.normal(500, 200, num_rows).round(2)
    sales = np.where(sales < 0, 0, sales)  # no negative sales
    
    # Create some relationships between variables
    discounts = np.random.uniform(0, 0.3, num_rows).round(2)
    discounts = np.where(categories == 'Electronics', discounts + 0.1, discounts)
    discounts = np.where(regions == 'West', discounts + 0.05, discounts)
    
    # Create dataframe
    data = {
        'Date': dates,
        'Category': categories,
        'Region': regions,
        'Sales': sales,
        'Discount': discounts,
        'Units_Sold': np.random.poisson(50, num_rows) + (sales/20).astype(int),
        'Customer_Rating': np.random.randint(1, 6, num_rows),
        'Returned': np.random.choice(['Yes', 'No'], size=num_rows, p=[0.1, 0.9])
    }
    
    return pd.DataFrame(data)

# Generate and save the sample data
df = generate_sample_data(200)
df.to_csv('sample_sales_data.csv', index=False)
print("Sample CSV file 'sample_sales_data.csv' created successfully!")