import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

class ExpenseandIncomeTracker:
    def __init__(self):
        self.expenses = self.load_data()

        # Sidebar for adding expenses
        st.sidebar.header('Add Expense & Income')
        self.date = st.sidebar.date_input('Date', value=datetime.today())
        self.category = st.sidebar.text_input('Category')
        self.amount = st.sidebar.number_input('Amount', min_value=0.00, step=0.01)
        self.expense_type = st.sidebar.selectbox('Expense Type', ['Expense', 'Income'])

        if st.sidebar.button('Add Value'):
            self.add_expense()

        # Convert 'Date' column to datetime format
        self.expenses['Date'] = pd.to_datetime(self.expenses['Date'])

        # Display the expenses with icons
        st.header('Expense & Income Tracker')

        # Display the DataFrame
        st.table(self.expenses.style.format({'Amount': "฿{:.2f}"}))

        # Display total income and expenses for the month
        current_month = datetime.now().month
        filtered_expenses = self.expenses[(self.expenses['Date'].dt.month == current_month)]

        # Display separate graphs for income and expenses with only bars
        st.subheader('Income and Expense Calendar')
        self.display_calendar_graph(filtered_expenses)

        st.subheader('Income Graph')
        self.display_bar_graph(filtered_expenses, 'Income', 'green')

        st.subheader('Expense Graph')
        self.display_bar_graph(filtered_expenses, 'Expense', 'red')

        # Add a delete button
        st.sidebar.header('Delete Data')
        delete_options = self.expenses['Date'].astype(str) + ' - ' + self.expenses['Category'] + ' (' + self.expenses['Type'] + ')'
        delete_expense = st.sidebar.selectbox('Select data to delete', options=delete_options, index=0)

        if st.sidebar.button('Delete Value'):
            self.delete_expense(delete_expense)

        # New page to show lists of income and expenses
        st.title('Income and Expense Lists')

        # Show list of income
        st.subheader('Income List')
        income_list = self.expenses[self.expenses['Type'] == 'Income'][['Date', 'Category', 'Amount']]
        st.table(income_list.style.format({'Amount': "${:.2f}"}))

        # Show list of expenses
        st.subheader('Expense List')
        expense_list = self.expenses[self.expenses['Type'] == 'Expense'][['Date', 'Category', 'Amount']]
        st.table(expense_list.style.format({'Amount': "${:.2f}"}))

    def load_data(self):
        try:
            return pd.read_csv('expenses.csv', parse_dates=['Date'])
        except FileNotFoundError:
            return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Type'])

    def add_expense(self):
        self.expenses = self.load_data()
        self.expenses = self.expenses.append({'Date': self.date, 'Category': self.category,
                                              'Amount': self.amount, 'Type': self.expense_type},
                                             ignore_index=True)
        st.sidebar.success('Value added successfully!')

        # Save data to CSV file
        self.expenses.to_csv('expenses.csv', index=False)

    def display_calendar_graph(self, filtered_expenses):
        fig_calendar = go.Figure()
        for expense_type, type_data in filtered_expenses.groupby('Type'):
            fig_calendar.add_trace(go.Bar(x=type_data['Date'], y=type_data['Amount'],
                                         name=expense_type, marker_color='green' if expense_type == 'Income' else 'red'))
        st.plotly_chart(fig_calendar)

    def display_bar_graph(self, filtered_expenses, graph_type, color):
        fig = go.Figure()
        for category, category_data in filtered_expenses[filtered_expenses['Type'] == graph_type].groupby('Category'):
            fig.add_trace(go.Bar(x=category_data['Date'], y=category_data['Amount'],
                                 name=category, marker_color=color))
        st.plotly_chart(fig)

    def delete_expense(self, selected_expense):
        self.expenses = self.load_data()  # Load the current state of data

        # Extracting information from selected_expense string
        date_str, rest = selected_expense.split(' - ')
        category, expense_type = rest.split(' (')[0], rest.split(' (')[1].split(')')[0]

        # Finding index of the expense to delete
        delete_index = self.expenses[
            (self.expenses['Date'].astype(str) == date_str) &
            (self.expenses['Category'] == category) &
            (self.expenses['Type'] == expense_type)
        ].index

        if len(delete_index) > 0:
            self.expenses = self.expenses.drop(index=delete_index)
            st.sidebar.success('Value deleted successfully!')
        else:
            st.sidebar.warning('Selected expense not found. Please try again.')

        # Save updated data to CSV file
        self.expenses.to_csv('expenses.csv', index=False)


if __name__ == "__main__":
    ExpenseandIncomeTracker()
