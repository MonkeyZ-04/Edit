import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


# Create or load the expenses DataFrame
def load_data():
    try:
        return pd.read_csv('expenses.csv', parse_dates=['Date'])
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Type'])


expenses = load_data()

# Sidebar for adding expenses
st.sidebar.header('Add Expense & Income')
date = st.sidebar.date_input('Date', value=datetime.today())
category = st.sidebar.text_input('Category')
amount = st.sidebar.number_input('Amount', min_value=0.01, step=0.01)
expense_type = st.sidebar.selectbox('Expense Type', ['Expense', 'Income'])

if st.sidebar.button('Add Value'):
    expenses = load_data()
    expenses = expenses.append({'Date': date, 'Category': category, 'Amount': amount, 'Type': expense_type},
                               ignore_index=True)
    st.sidebar.success('Value added successfully!')

    # Save data to CSV file
    expenses.to_csv('expenses.csv', index=False)

# Convert 'Date' column to datetime format
expenses['Date'] = pd.to_datetime(expenses['Date'])

# Display the expenses with icons
st.header('Expense & Income Tracker')

# Display the DataFrame
st.table(expenses.style.format({'Amount': "฿{:.2f}"}))

# Display total income and expenses for the month
current_month = datetime.now().month
filtered_expenses = expenses[(expenses['Date'].dt.month == current_month)]


# Display separate graphs for income and expenses with only bars
st.subheader('Income and Expense Calendar')
fig_calendar = go.Figure()
for expense_type, type_data in filtered_expenses.groupby('Type'):
    fig_calendar.add_trace(go.Bar(x=type_data['Date'], y=type_data['Amount'], name=expense_type, marker_color='green' if expense_type == 'Income' else 'red'))
st.plotly_chart(fig_calendar)

st.plotly_chart(fig_calendar)
st.subheader('Income Graph')
fig_income = go.Figure()
for category, category_data in filtered_expenses[filtered_expenses['Type'] == 'Income'].groupby('Category'):
    fig_income.add_trace(go.Scatter(x=category_data['Date'], y=category_data['Amount'],
                                    mode='lines+markers', name=category, marker=dict(color='green')))
st.plotly_chart(fig_income)

st.subheader('Expense Graph')
fig_expense = go.Figure()
for category, category_data in filtered_expenses[filtered_expenses['Type'] == 'Expense'].groupby('Category'):
    fig_expense.add_trace(go.Scatter(x=category_data['Date'], y=category_data['Amount'],
                                     mode='lines+markers', name=category, marker=dict(color='red')))
st.plotly_chart(fig_expense)

# Display calendar with income and expenses graph


# Add a delete button
st.sidebar.header('Delete Expense')
max_value = len(expenses) - 1 if len(expenses) > 0 else 0
delete_index = st.sidebar.number_input('Enter index to delete', min_value=0, max_value=max_value, value=0, step=1)

if st.sidebar.button('Delete Value'):
    expenses = load_data()
    expenses = expenses.drop(index=delete_index)
    st.sidebar.success('Value deleted successfully!')

    # Save updated data to CSV file
    expenses.to_csv('expenses.csv', index=False)

# New page to show lists of income and expenses
st.title('Income and Expense Lists')

# Show list of income
st.subheader('Income List')
income_list = expenses[expenses['Type'] == 'Income'][['Date', 'Category', 'Amount']]
st.table(income_list.style.format({'Amount': "${:.2f}"}))

# Show list of expenses
st.subheader('Expense List')
expense_list = expenses[expenses['Type'] == 'Expense'][['Date', 'Category', 'Amount']]
st.table(expense_list.style.format({'Amount': "${:.2f}"}))
