# data_manager.py
import pandas as pd

class Data:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        try:
            self.df = pd.read_csv(csv_file_path)
            self.df['Date'] = pd.to_datetime(self.df['Date']).dt.date
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['Date', 'Type', 'Category', 'Amount'])

    def save_to_csv(self):
        self.df.to_csv(self.csv_file_path, index=False)

    def add_data(self, date_val, type_val, category_val, amount_val):
        new_entry = {'Date': date_val, 'Type': type_val, 'Category': category_val, 'Amount': amount_val}
        self.df = pd.concat([self.df, pd.DataFrame([new_entry])], ignore_index=True)

    def delete_data(self, selected_index):
        self.df = self.df.drop(selected_index)

    def get_category_list(self, transaction_type):
        return self.df[self.df['Type'] == transaction_type]['Category'].unique()
