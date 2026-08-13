import os
import pandas as pd

def create_budget_file():
    # Create a dictionary with dummy data
    data = {
        'Item': ['Item1', 'Item2', 'Item3', 'Item4', 'Item5'],
        'Cost': [10.99, 5.99, 7.99, 3.99, 9.99],
        'Category': ['Food', 'Entertainment', 'Clothing', 'Electronics', 'Home']
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Get the path to the desktop
    desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

    # Create the file path
    file_path = os.path.join(desktop_path, 'Budget.xlsx')

    # Write the DataFrame to an Excel file
    df.to_excel(file_path, index=False)

    print("Budget file created successfully.")

if __name__ == "__main__":
    create_budget_file()