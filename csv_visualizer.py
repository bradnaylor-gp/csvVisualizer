import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import calendar
import re

def load_and_process_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Remove the total rows
    df = df[~df['AP Period'].isin(['01 January TOTAL', '02 February TOTAL', 'GRAND TOTAL'])]
    
    # Function to clean currency strings
    def clean_currency(x):
        # Handle both string and numeric inputs
        if isinstance(x, str):
            return float(x.replace('$', '').replace(',', ''))
        return float(x)
    
    # Apply currency cleaning
    df['Amount'] = df['Amount'].apply(clean_currency)
    
    return df

def categorize_expenses(df):
    # Function to extract the main category from the account name
    def extract_main_category(account_name):
        # Split the account name and take the first part
        parts = account_name.split(':')
        return parts[0].strip()
    
    # Create a new column with the main category
    df['Expense Category'] = df['Account Name'].apply(extract_main_category)
    
    return df

def generate_comprehensive_report(df):
    # Prepare report dictionary
    report = {
        'Revenue': {},
        'Expenses': {},
        'Detailed Expenses': {},
        'Net Revenue': {},
        'Hourly Expenses': {},
        'Expense Categories': []
    }

    # Get all unique names
    all_names = df['Name'].unique()

    # Identify and calculate revenue (Cross Charge entries)
    revenue_df = df[df['Account Name'].str.contains('Cross Charge', case=False) & (df['Amount'] > 0)]
    revenue_by_person = revenue_df.groupby('Name')['Amount'].sum()
    
    # Ensure all names are in the revenue dictionary with at least 0
    for name in all_names:
        report['Revenue'][name] = revenue_by_person.get(name, 0)

    # Calculate Total Expenses (negative amounts)
    expense_df = df[df['Amount'] < 0]
    total_expenses_by_person = expense_df.groupby('Name')['Amount'].sum()
    report['Expenses'] = total_expenses_by_person.to_dict()

    # Identify expense categories dynamically
    expense_categories = df[df['Amount'] < 0]['Expense Category'].unique().tolist()
    report['Expense Categories'] = expense_categories

    # Detailed Expense Breakdown by Category
    for category in expense_categories:
        category_df = expense_df[expense_df['Expense Category'] == category]
        category_expenses = category_df.groupby('Name')['Amount'].sum()
        report['Detailed Expenses'][category] = category_expenses.to_dict()

    # Net Revenue Calculation (careful handling of zero and negative amounts)
    net_revenue = {}
    for name in all_names:
        revenue = report['Revenue'].get(name, 0)
        expenses = report['Expenses'].get(name, 0)
        net_revenue[name] = revenue + expenses  # Add because expenses are negative
    report['Net Revenue'] = net_revenue

    # Total Revenue Calculation
    total_revenue = revenue_by_person.sum()
    report['Total Revenue'] = total_revenue

    # Total Expenses Calculation
    total_expenses = total_expenses_by_person.sum()
    report['Total Expenses'] = total_expenses

    # Profit/Loss Calculation
    report['Profit/Loss'] = total_revenue + total_expenses

    # Determine the number of days in the period (assuming current month)
    # Use the last row's AP Period to determine the month
    current_month = df['AP Period'].iloc[-1].split()[1]
    _, days_in_month = calendar.monthrange(2024, list(calendar.month_name).index(current_month))

    # Hourly Expenses Calculation (accounting for actual workdays)
    # Assume 8 working hours per day, excluding weekends
    workdays = sum(1 for day in range(1, days_in_month + 1) 
                   if calendar.weekday(2024, list(calendar.month_name).index(current_month), day) < 5)
    total_working_hours = workdays * 8

    hourly_expenses = {}
    for name, expenses in total_expenses_by_person.items():
        hourly_expenses[name] = abs(expenses) / total_working_hours
    report['Hourly Expenses'] = hourly_expenses

    return report


def create_visualizations(df, report):
    # Ensuring output folder exists
    output_folder = 'Financial_Analysis'
    os.makedirs(output_folder, exist_ok=True)

    # Revenue Visualization (Bottom to Top)
    plt.figure(figsize=(12, 6))
    revenue_df = pd.DataFrame.from_dict(report['Revenue'], orient='index', columns=['Revenue'])
    revenue_df.index.name = 'Name'
    revenue_df.reset_index(inplace=True)
    revenue_df = revenue_df.sort_values('Revenue')
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='Revenue', y='Name', data=revenue_df, orient='h')
    plt.title('Monthly Revenue by Employee')
    plt.xlabel('Revenue ($)')
    plt.ylabel('Employee')
    
    # Add value labels
    for i, v in enumerate(revenue_df['Revenue']):
        ax.text(v, i, f'${v:,.2f}', va='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'revenue_visualization.png'))
    plt.close()

    # Detailed Expenses Pie Charts per Employee
    for name in report['Detailed Expenses'][list(report['Detailed Expenses'].keys())[0]].keys():
        plt.figure(figsize=(10, 10))
        # Gather expenses for this employee
        employee_expenses = {}
        for category, expenses in report['Detailed Expenses'].items():
            employee_expenses[category] = abs(expenses.get(name, 0))
        
        # Remove categories with zero expenses
        employee_expenses = {k:v for k,v in employee_expenses.items() if v > 0}
        
        plt.pie(employee_expenses.values(), labels=[f'{k}: ${v:,.2f}' for k,v in employee_expenses.items()], 
                autopct='%1.1f%%')
        plt.title(f'Expense Breakdown for {name}')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{name}_expenses_pie.png'))
        plt.close()

    # Expenses Bar Chart (Bottom to Top)
    expenses_data = []
    for category, category_expenses in report['Detailed Expenses'].items():
        for name, amount in category_expenses.items():
            expenses_data.append({
                'Name': name, 
                'Category': category, 
                'Amount': abs(amount)
            })
    
    expenses_df = pd.DataFrame(expenses_data)
    expenses_pivot = expenses_df.pivot(index='Name', columns='Category', values='Amount').fillna(0)
    expenses_pivot = expenses_pivot.sort_values(by=expenses_pivot.columns.tolist(), ascending=True)
    
    plt.figure(figsize=(14, 8))
    expenses_pivot.plot(kind='barh', stacked=True)
    plt.title('Detailed Expenses by Category')
    plt.xlabel('Expenses ($)')
    plt.ylabel('Employee')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'detailed_expenses_visualization.png'))
    plt.close()

    # Net Revenue Visualization (Bottom to Top)
    net_revenue_df = pd.DataFrame.from_dict(report['Net Revenue'], orient='index', columns=['Net Revenue'])
    net_revenue_df.index.name = 'Name'
    net_revenue_df.reset_index(inplace=True)
    net_revenue_df = net_revenue_df.sort_values('Net Revenue')
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='Net Revenue', y='Name', data=net_revenue_df, orient='h')
    plt.title('Net Revenue by Employee')
    plt.xlabel('Net Revenue ($)')
    plt.ylabel('Employee')
    
    # Add value labels
    for i, v in enumerate(net_revenue_df['Net Revenue']):
        ax.text(v, i, f'${v:,.2f}', va='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'net_revenue_visualization.png'))
    plt.close()

    # Hourly Expenses Visualization (Bottom to Top)
    hourly_expenses_df = pd.DataFrame.from_dict(report['Hourly Expenses'], orient='index', columns=['Hourly Expenses'])
    hourly_expenses_df.index.name = 'Name'
    hourly_expenses_df.reset_index(inplace=True)
    hourly_expenses_df = hourly_expenses_df.sort_values('Hourly Expenses')
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='Hourly Expenses', y='Name', data=hourly_expenses_df, orient='h')
    plt.title('Hourly Expenses by Employee')
    plt.xlabel('Hourly Expenses ($)')
    plt.ylabel('Employee')
    
    # Add value labels
    for i, v in enumerate(hourly_expenses_df['Hourly Expenses']):
        ax.text(v, i, f'${v:,.2f}', va='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'hourly_expenses_visualization.png'))
    plt.close()

def generate_markdown_report(report):
    output_folder = 'Financial_Analysis'
    os.makedirs(output_folder, exist_ok=True)
    
    with open(os.path.join(output_folder, 'financial_report.md'), 'w') as f:
        # Title
        f.write("# Financial Analysis Report\n\n")
        
        # Revenue Section
        f.write("## Revenue\n")
        f.write(f"**Total Revenue: ${report['Total Revenue']:,.2f}**\n\n")
        f.write("### Monthly Revenue by Employee\n")
        for name, revenue in sorted(report['Revenue'].items(), key=lambda x: x[1]):
            f.write(f"- {name}: ${revenue:,.2f}\n")
        f.write("\n")

        # Expenses Section
        f.write("## Expenses\n")
        f.write(f"**Total Expenses: ${report['Total Expenses']:,.2f}**\n\n")
        
        # Detailed Expenses
        f.write("### Detailed Expenses by Category\n")
        for category in report['Expense Categories']:
            f.write(f"#### {category}\n")
            category_expenses = report['Detailed Expenses'][category]
            for name, amount in sorted(category_expenses.items(), key=lambda x: x[1]):
                f.write(f"- {name}: ${abs(amount):,.2f}\n")
            f.write("\n")

        # Net Revenue
        f.write("## Net Revenue\n")
        for name, net_revenue in sorted(report['Net Revenue'].items(), key=lambda x: x[1]):
            f.write(f"- {name}: ${net_revenue:,.2f}\n")
        f.write("\n")

        # Hourly Expenses
        f.write("## Hourly Expenses\n")
        for name, cost in sorted(report['Hourly Expenses'].items(), key=lambda x: x[1]):
            f.write(f"- {name}: ${cost:,.2f}\n")
        f.write("\n")

        # Profit/Loss
        f.write("## Financial Summary\n")
        f.write(f"**Profit/Loss: ${report['Profit/Loss']:,.2f}**\n")

def main(file_path):
    # Load and process data
    df = load_and_process_data(file_path)
    
    # Categorize expenses dynamically
    df = categorize_expenses(df)
    
    # Generate comprehensive report
    report = generate_comprehensive_report(df)
    
    # Create visualizations
    create_visualizations(df, report)
    
    # Generate markdown report
    generate_markdown_report(report)
    
    # Print key findings
    print("Financial Analysis Complete!")
    print(f"Total Revenue: ${report['Total Revenue']:,.2f}")
    print(f"Total Expenses: ${report['Total Expenses']:,.2f}")
    print(f"Profit/Loss: ${report['Profit/Loss']:,.2f}")
    print("\nDetected Expense Categories:")
    for category in report['Expense Categories']:
        print(f"- {category}")

# Run the analysis
main('Book1.csv')