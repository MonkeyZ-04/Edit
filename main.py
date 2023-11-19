import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


class Data:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        try:
            self.df = pd.read_csv(csv_file_path)

            # Convert 'Date' column to datetime.date
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


class Display:
    def show_data(self, df):
        st.write('### Transaction')
        sort_options = ['No Sorting', 'Date', 'Amount']
        sort_selected = st.selectbox('Sort Options', sort_options, index=0)
        sort_order_options = ['Ascending', 'Descending']
        sort_order = st.selectbox('Sort Order', sort_order_options, index=0)
        ascending = (sort_order == 'Ascending')
        if sort_selected == 'Date':
            df.sort_values(by='Date', inplace=True, ascending=ascending)
        elif sort_selected == 'Amount':
            df.sort_values(by='Amount', inplace=True, ascending=ascending)

        page_df = df.copy()
        page_df.index = range(1, len(page_df) + 1)
        page_df = page_df.rename_axis('Index')
        page_df['Amount'] = page_df['Amount'].apply(lambda x: '{:.2f}'.format(x))
        st.dataframe(page_df, width=800)

    def plot_bar_chart_comparison(self, df, x_col, y_col, title, start_date, end_date):
        df_income = df[df['Type'] == 'Income'].groupby(x_col)[y_col].sum().reset_index()
        df_expense = df[df['Type'] == 'Expense'].groupby(x_col)[y_col].sum().reset_index()
        df_total = pd.merge(df_income, df_expense, on=x_col, how='outer', suffixes=('_Income', '_Expense')).fillna(0)

        df_filtered = df_total[(df_total[x_col] >= start_date) & (df_total[x_col] <= end_date)]
        df_filtered = df_filtered.sort_values(by=[x_col])
        min_date = df_filtered[x_col].min()
        df_filtered = df_filtered[df_filtered[x_col] >= min_date]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=df_filtered[x_col], y=df_filtered[y_col + '_Income'], name='Total Income', marker_color='green'))
        fig.add_trace(
            go.Bar(x=df_filtered[x_col], y=df_filtered[y_col + '_Expense'], name='Total Expense', marker_color='red'))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_col),
            yaxis=dict(title='Total Amount'),
        )

        st.plotly_chart(fig)

    def plot_line_chart_comparison(self, df, x_col, y_col, title, start_date, end_date):
        df_income = df[df['Type'] == 'Income'].groupby(x_col)[y_col].sum().reset_index()
        df_expense = df[df['Type'] == 'Expense'].groupby(x_col)[y_col].sum().reset_index()
        df_total = pd.merge(df_income, df_expense, on=x_col, how='outer', suffixes=('_Income', '_Expense')).fillna(0)
        df_total['Total'] = df_total[y_col + '_Income'] - df_total[y_col + '_Expense']

        df_filtered = df_total[(df_total[x_col] >= start_date) & (df_total[x_col] <= end_date)]
        df_filtered = df_filtered.sort_values(by=[x_col])
        min_date = df_filtered[x_col].min()
        df_filtered = df_filtered[df_filtered[x_col] >= min_date]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df_filtered[x_col], y=df_filtered[y_col + '_Income'], mode='lines', name='Income',
                                 line=dict(color='green')))
        fig.add_trace(go.Scatter(x=df_filtered[x_col], y=df_filtered[y_col + '_Expense'], mode='lines', name='Expense',
                                 line=dict(color='red')))
        fig.add_trace(
            go.Scatter(x=df_filtered[x_col], y=df_filtered['Total'], mode='lines', name='net', line=dict(color='blue')))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_col),
            yaxis=dict(title='Total Amount'),
        )

        st.plotly_chart(fig)

    def plot_pie_chart_comparison(self, df, x_col, y_col, title, start_date, end_date):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date)]
        df_grouped = df_filtered.groupby('Type')[y_col].sum().reset_index()

        fig = go.Figure()
        fig.add_trace(go.Pie(labels=df_grouped['Type'], values=df_grouped[y_col], marker=dict(colors=['red', 'green'])))
        fig.update_layout(
            title=title,
            showlegend=True,
        )

        st.plotly_chart(fig)

    def plot_waterfall_chart_comparison(self, df, x_col, y_col, title, start_date, end_date):
        df_income = df[df['Type'] == 'Income'].groupby(x_col)[y_col].sum().reset_index()
        df_expense = df[df['Type'] == 'Expense'].groupby(x_col)[y_col].sum().reset_index()
        df_total = pd.merge(df_income, df_expense, on=x_col, how='outer', suffixes=('_Income', '_Expense')).fillna(0)
        df_total['Total'] = df_total[y_col + '_Income'] - df_total[y_col + '_Expense']

        df_filtered = df_total[(df_total[x_col] >= start_date) & (df_total[x_col] <= end_date)]
        df_filtered = df_filtered.sort_values(by=[x_col])
        min_date = df_filtered[x_col].min()
        df_filtered = df_filtered[df_filtered[x_col] >= min_date]

        fig = go.Figure(go.Waterfall(
            name="Total",
            orientation="v",
            measure=["relative"] * len(df_filtered),
            x=df_filtered[x_col],
            textposition="outside",
            text=df_filtered['Total'],
            y=df_filtered['Total'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_col),
            yaxis=dict(title='Amount'),
            showlegend=True,
        )

        st.plotly_chart(fig)

    def plot_stacked_bar_chart_income(self, df, x_col, y_col, title, start_date, end_date):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date) & (df['Type'] == 'Income')]
        fig = go.Figure()
        categories = df_filtered['Category'].unique()
        for category in categories:
            category_df = df_filtered[df_filtered['Category'] == category]
            fig.add_trace(go.Bar(x=category_df[x_col], y=category_df[y_col], name=category))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_col),
            yaxis=dict(title='Total Amount'),
            barmode='stack',
        )

        st.plotly_chart(fig)

    def plot_pie_chart_income(self, df, x_col, y_col, title, start_date, end_date):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date) & (df['Type'] == 'Income')]
        categories = df_filtered['Category'].unique()
        total_amounts = df_filtered.groupby('Category')[y_col].sum()

        fig = go.Figure(data=[go.Pie(labels=total_amounts.index, values=total_amounts.values)])
        fig.update_layout(
            title=title,
            showlegend=True,
        )

        st.plotly_chart(fig)

    def plot_stacked_bar_chart_expense(self, df, x_col, y_col, title, start_date, end_date):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date) & (df['Type'] == 'Expense')]
        fig = go.Figure()
        categories = df_filtered['Category'].unique()
        for category in categories:
            category_df = df_filtered[df_filtered['Category'] == category]
            fig.add_trace(go.Bar(x=category_df[x_col], y=category_df[y_col], name=category))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_col),
            yaxis=dict(title='Total Amount'),
            barmode='stack',
        )

        st.plotly_chart(fig)

    def plot_pie_chart_expense(self, df, x_col, y_col, title, start_date, end_date):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date) & (df['Type'] == 'Expense')]
        categories = df_filtered['Category'].unique()
        total_amounts = df_filtered.groupby('Category')[y_col].sum()

        fig = go.Figure(data=[go.Pie(labels=total_amounts.index, values=total_amounts.values)])
        fig.update_layout(
            title=title,
            showlegend=True,
        )

        st.plotly_chart(fig)


class App:
    def __init__(self, data, display):
        self.data = data
        self.display = display
        self.income_category_list = self.get_category_list('Income')
        self.expense_category_list = self.get_category_list('Expense')

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
                                                 max_value=valid_indices[-1], value=valid_indices[0], step=1, key='delete')

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
                                           min_value=pd.to_datetime(self.data.df['Date'].min(), errors='coerce'))
        end_date = st.sidebar.date_input("End Date",
                                         max_value=pd.to_datetime(self.data.df['Date'].max(), errors='coerce'),
                                         value=pd.to_datetime('today'))

        filtered_df = self.data.df[
            (self.data.df['Date'].notna()) & (self.data.df['Date'] >= start_date) & (self.data.df['Date'] <= end_date)]

        transaction_type = st.sidebar.selectbox('Choose Transaction Type', ['Income vs Expense', 'Income', 'Expense'])
        graph_types_income_expense = ['Bar Chart', 'Line Chart', 'Pie Chart', 'Waterfall Chart']
        graph_types_income = ['Stacked Chart', 'Pie Chart']
        graph_types_expense = ['Stacked Chart', 'Pie Chart']

        if transaction_type == 'Income vs Expense':
            graph_type = st.sidebar.selectbox('Choose Graph Type', graph_types_income_expense)
            if graph_type == 'Bar Chart':
                self.display.plot_bar_chart_comparison(filtered_df, 'Date', 'Amount', 'Income vs Expense', start_date,
                                                       end_date)
            elif graph_type == 'Line Chart':
                self.display.plot_line_chart_comparison(filtered_df, 'Date', 'Amount', 'Income vs Expense', start_date,
                                                        end_date)
            elif graph_type == 'Pie Chart':
                self.display.plot_pie_chart_comparison(filtered_df, 'Date', 'Amount', 'Income vs Expense', start_date,
                                                       end_date)
            elif graph_type == 'Waterfall Chart':
                self.display.plot_waterfall_chart_comparison(filtered_df, 'Date', 'Amount', 'Income vs Expense',
                                                             start_date, end_date)

        elif transaction_type == 'Income':
            graph_type = st.sidebar.selectbox('Choose Graph Type', graph_types_income)
            if graph_type == 'Stacked Chart':
                self.display.plot_stacked_bar_chart_income(filtered_df, 'Date', 'Amount', 'Income Categories',
                                                           start_date, end_date)
            elif graph_type == 'Pie Chart':
                self.display.plot_pie_chart_income(filtered_df, 'Date', 'Amount', 'Income Categories', start_date,
                                                   end_date)

        elif transaction_type == 'Expense':
            graph_type = st.sidebar.selectbox('Choose Graph Type', graph_types_expense)
            if graph_type == 'Stacked Chart':
                self.display.plot_stacked_bar_chart_expense(filtered_df, 'Date', 'Amount', 'Expense Categories',
                                                            start_date, end_date)
            elif graph_type == 'Pie Chart':
                self.display.plot_pie_chart_expense(filtered_df, 'Date', 'Amount', 'Expense Categories', start_date,
                                                    end_date)

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