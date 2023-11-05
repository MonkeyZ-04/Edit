import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import base64


class ExpenseandIncomeTracker:
    def __init__(self):
        self.expenses = self.load_data()
        self.setup_sidebar()
        self.setup_expense_header()
        self.setup_expense_display()
        self.setup_delete_data()
        self.display_income_expense_lists()

    def load_data(self):
        try:
            return pd.read_csv('expenses.csv', parse_dates=['Date'])
        except FileNotFoundError:
            return pd.DataFrame(columns=['Date', 'Icon', 'Amount', 'Type'])

    def setup_sidebar(self):

        img = "img.png"
        image_data = open(img, "rb").read()
        image_base64 = base64.b64encode(image_data).decode()
        st.sidebar.markdown(
            f'<div style="display: flex; justify-content: center; align-items: center;">'
            f'<img src="data:image/png;base64,{image_base64}" style="width:300px; height:200px;">'
            f'</div>',
            unsafe_allow_html=True
        )
        st.sidebar.header('Add Expense & Income')
        self.date = st.sidebar.date_input('Date', value=datetime.today())
        self.icon_category = st.sidebar.selectbox('Select Icon', ['💰', '🛒', '🍔', '🚗', '💡'])  # Add more icons as needed
        self.amount = st.sidebar.number_input('Amount', min_value=0.00, step=0.01)
        self.expense_type = st.sidebar.selectbox('Expense Type', ['Expense', 'Income'])

        if st.sidebar.button('Add Value'):
            self.add_expense()

        self.expenses['Date'] = pd.to_datetime(self.expenses['Date'])

    def setup_expense_header(self):
        st.header('Expense & Income Tracker')

    def setup_expense_display(self):
        rows_per_page = 10
        total_rows = len(self.expenses)
        page_number = st.radio("Select Page", list(range(1, total_rows // rows_per_page + 2)), index=1)
        start_index = (page_number - 1) * rows_per_page
        end_index = min(page_number * rows_per_page, total_rows)

        st.table(self.expenses[start_index:end_index].style.format({'Amount': "฿{:.2f}"}))

        current_month = datetime.now().month
        filtered_expenses = self.expenses[(self.expenses['Date'].dt.month == current_month)]
        st.subheader('Income and Expense Calendar')
        self.display_calendar_graph(filtered_expenses)

        st.subheader('Income Graph')
        self.display_graph('Income', filtered_expenses)

        st.subheader('Expense Graph')
        self.display_graph('Expense', filtered_expenses)

    def display_calendar_graph(self, filtered_expenses):
        fig_calendar = go.Figure()
        for expense_type, type_data in filtered_expenses.groupby('Type'):
            fig_calendar.add_trace(go.Bar(x=type_data['Date'], y=type_data['Amount'],
                                          name=expense_type,
                                          marker_color='green' if expense_type == 'Income' else 'red'))

        chart = st.plotly_chart(fig_calendar, use_container_width=True)
        st.subheader('Filter by Date Range')
        start_date = st.date_input("Start Date", min_value=filtered_expenses['Date'].min(),
                                   max_value=filtered_expenses['Date'].max(), value=filtered_expenses['Date'].min(),
                                   format="YYYY-MM-DD")
        end_date = st.date_input("End Date", min_value=filtered_expenses['Date'].min(),
                                 max_value=filtered_expenses['Date'].max(), value=filtered_expenses['Date'].max(),
                                 format="YYYY-MM-DD")

        if start_date > end_date:
            st.error("Start date should be less than or equal to end date.")
        else:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            filtered_expenses = self.expenses[
                (self.expenses['Date'] >= start_date) & (self.expenses['Date'] <= end_date)]

            fig_calendar.data = []
            for expense_type, type_data in filtered_expenses.groupby('Type'):
                fig_calendar.add_trace(go.Bar(x=type_data['Date'], y=type_data['Amount'],
                                              name=expense_type,
                                              marker_color='green' if expense_type == 'Income' else 'red'))

            chart.plotly_chart(fig_calendar, use_container_width=True)

    def display_graph(self, graph_type, filtered_expenses):
        unique_icons = filtered_expenses[filtered_expenses['Type'] == graph_type]['Icon'].unique()
        unique_icons = ['All'] + list(unique_icons)
        selected_icon = st.selectbox(f'Select {graph_type} Icon', unique_icons)

        if selected_icon == 'All':
            filtered_data = filtered_expenses[(filtered_expenses['Type'] == graph_type)]
        else:
            filtered_data = filtered_expenses[
                (filtered_expenses['Type'] == graph_type) &
                (filtered_expenses['Icon'] == selected_icon)
                ]

        fig = go.Figure()

        n_icons = len(unique_icons)
        base_color = 'green' if graph_type == 'Income' else 'red'
        colors = [f'rgb(0, {i * (255 // n_icons)}, 0)' for i in range(n_icons)] if graph_type == 'Income' else [
            f'rgb({i * (255 // n_icons)}, 0, 0)' for i in range(n_icons)]
        icon_colors = dict(zip(unique_icons, colors))

        for icon, icon_data in filtered_data.groupby('Icon'):
            fig.add_trace(go.Bar(x=icon_data['Date'], y=icon_data['Amount'],
                                 name=icon, marker_color=icon_colors[icon]))

        st.plotly_chart(fig)

    def setup_delete_data(self):
        st.sidebar.header('Delete Data')
        delete_options = self.expenses['Date'].astype(str) + ' - ' + self.expenses['Icon'] + ' (' + self.expenses['Type'] + ')'
        self.delete_expense = st.sidebar.selectbox('Select data to delete', options=delete_options, index=0)

        if st.sidebar.button('Delete Value'):
            self.delete_expense()

    def display_income_expense_lists(self):
        st.title('Income and Expense Lists')

        st.subheader('Income List')
        income_list = self.expenses[self.expenses['Type'] == 'Income'][['Date', 'Icon', 'Amount']]
        st.table(income_list.style.format({'Amount': "${:.2f}"}))

        st.subheader('Expense List')
        expense_list = self.expenses[self.expenses['Type'] == 'Expense'][['Date', 'Icon', 'Amount']]
        st.table(expense_list.style.format({'Amount': "${:.2f}"}))

    def add_expense(self):
        self.expenses = self.load_data()
        self.expenses = self.expenses.append({'Date': self.date, 'Icon': self.icon_category,
                                              'Amount': self.amount, 'Type': self.expense_type},
                                             ignore_index=True)
        st.sidebar.success('Value added successfully!')
        self.expenses.to_csv('expenses.csv', index=False)

    def delete_expense(self):
        self.expenses = self.load_data()
        date_str, rest = self.delete_expense.split(' - ')
        icon, expense_type = rest.split(' (')[0], rest.split(' (')[1].split(')')[0]

        delete_index = self.expenses[
            (self.expenses['Date'].astype(str) == date_str) &
            (self.expenses['Icon'] == icon) &
            (self.expenses['Type'] == expense_type)
        ].index

        if len(delete_index) > 0:
            self.expenses = self.expenses.drop(index=delete_index)
            st.sidebar.success('Value deleted successfully!')
        else:
            st.sidebar.warning('Selected expense not found. Please try again.')

        self.expenses.to_csv('expenses.csv', index=False)


if __name__ == "__main__":
    ExpenseandIncomeTracker()
