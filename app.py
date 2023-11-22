# app.py
import pandas as pd
from data_manager import Data
from display_manager import Display
import streamlit as st


class App:
    def __init__(self, data, display):
        self.data = data
        self.display = display
        self.income_category_list = self.data.get_category_list('Income')
        self.expense_category_list = self.data.get_category_list('Expense')

    def get_category_list(self, transaction_type):
        return self.data.df[self.data.df['Type'] == transaction_type]['Category'].unique()

    def add_data(self):
        st.title('Add New Transaction')
        date_val = st.date_input('Date', value=pd.to_datetime('today').date())
        type_val = st.selectbox('Type', ['Income', 'Expense'])

        if type_val == 'Income':
            category_list = list(self.income_category_list) + ['Create New Category']
        else:
            category_list = list(self.expense_category_list) + ['Create New Category']

        category_val = st.selectbox('Category', category_list)

        if category_val == 'Create New Category':
            new_category = st.text_input('New Category').strip().capitalize()
            if new_category:
                category_val = new_category

        amount_val = st.number_input('Amount', value=0.0, format="%.2f")

        if st.button('Add transaction'):
            self.data.add_data(date_val, type_val, category_val, amount_val)
            self.income_category_list = self.get_category_list('Income')
            self.expense_category_list = self.get_category_list('Expense')
            st.success('Transaction added successfully.')

    def delete_data(self):
        st.sidebar.write('### Delete Transaction')
        valid_indices = range(1, len(self.data.df) + 1)
        selected_index = st.sidebar.number_input('Enter the index to delete', min_value=valid_indices[0],
                                                 max_value=valid_indices[-1], value=valid_indices[0], step=1,
                                                 key='delete')

        if st.sidebar.button('Delete transaction'):
            self.data.delete_data(selected_index - 1)
            st.sidebar.success('Transaction deleted.')

    def analyze_data(self):
        st.title('Data Analysis')

        # Filter out NaT values in 'Date' column
        valid_dates = self.data.df['Date'].dropna()

        if valid_dates.empty:
            st.warning("No valid dates found. Please review your data.")
            return

        start_date = st.sidebar.date_input("Start Date",
                                           min_value=pd.to_datetime(self.data.df['Date'].min(), errors='coerce'),
                                           value=pd.to_datetime(self.data.df['Date'].min(), errors='coerce'))
        end_date = st.sidebar.date_input("End Date",
                                         max_value=pd.to_datetime(self.data.df['Date'].max(), errors='coerce'),
                                         value=pd.to_datetime(self.data.df['Date'].max(), errors='coerce'))

        filtered_df = self.data.df[
            (self.data.df['Date'].notna()) & (self.data.df['Date'] >= start_date) & (self.data.df['Date'] <= end_date)]

        transaction_type = st.sidebar.selectbox('Choose Transaction Type', ['Income vs Expense', 'Income', 'Expense'])
        graph_types_income_expense = ['Bar Chart', 'Line Chart', 'Waterfall Chart']
        graph_types_income = ['Stacked Chart', 'Pie Chart']
        graph_types_expense = ['Stacked Chart', 'Pie Chart']

        if transaction_type == 'Income vs Expense':
            graph_type = st.sidebar.selectbox('Choose Graph Type', graph_types_income_expense)
            time_granularity_options = ['Daily', 'Weekly', 'Monthly', 'Yearly']
            time_granularity = st.sidebar.selectbox('Choose Time Granularity', time_granularity_options)
            if graph_type == 'Bar Chart':
                self.display.plot_bar(filtered_df, 'Date', 'Amount', 'Income vs Expense', start_date, end_date,
                                      time_granularity)
            elif graph_type == 'Line Chart':
                self.display.plot_line(filtered_df, 'Date', 'Amount', 'Income vs Expense', start_date, end_date,
                                       time_granularity)
            elif graph_type == 'Waterfall Chart':
                self.display.plot_waterfall(filtered_df, 'Date', 'Amount', 'Income vs Expense', start_date, end_date,
                                            time_granularity)

        elif transaction_type == 'Income':
            graph_type = st.sidebar.selectbox('Choose Graph Type', graph_types_income)
            if graph_type == 'Stacked Chart':
                self.display.plot_stacked(filtered_df, 'Date', 'Amount', 'Income Chart', start_date, end_date, 'Type',
                                          'Income')
            elif graph_type == 'Pie Chart':
                self.display.plot_pie(filtered_df, 'Date', 'Amount', 'Expense Chart', start_date, end_date, 'Type',
                                      'Income')

        elif transaction_type == 'Expense':
            graph_type = st.sidebar.selectbox('Choose Graph Type', graph_types_expense)
            if graph_type == 'Stacked Chart':
                self.display.plot_stacked(filtered_df, 'Date', 'Amount', 'Income Chart', start_date, end_date, 'Type',
                                          'Expense')
            elif graph_type == 'Pie Chart':
                self.display.plot_pie(filtered_df, 'Date', 'Amount', 'Expense Chart', start_date, end_date, 'Type',
                                      'Expense')

    def run(self):
        st.sidebar.image('img.png', width=250)
        option = st.sidebar.radio("Select Operation", ("Add Transaction", "View Transaction", "Analyse"))

        if option == "Add Transaction":
            self.add_data()
        elif option == "View Transaction":
            self.display.show_data(self.data.df)
            self.delete_data()
        elif option == "Analyse":
            self.analyze_data()

        self.data.save_to_csv()


if __name__ == "__main__":
    csv_file_path = 'your_data.csv'
    App(Data(csv_file_path), Display()).run()