# display_manager.py
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


class Display:

    def show_data(self, df):
        st.write('### Transaction')
        sort_options = ['Date', 'Amount', 'Category', 'Type']
        sort_selected = st.selectbox('Sort Options', sort_options, index=0)
        sort_order_options = ['Ascending', 'Descending']
        sort_order = st.selectbox('Sort Order', sort_order_options, index=0)
        ascending = (sort_order == 'Ascending')
        if sort_selected == 'Date':
            start_date = st.date_input('Start Date', min_value=df['Date'].min(), max_value=df['Date'].max(),
                                       value=df['Date'].min())
            end_date = st.date_input('End Date', min_value=df['Date'].min(), max_value=df['Date'].max(),
                                     value=df['Date'].max())
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            df.sort_values(by='Date', inplace=True, ascending=ascending)
        elif sort_selected == 'Amount':
            df.sort_values(by='Amount', inplace=True, ascending=ascending)
        elif sort_selected == 'Category':
            df.sort_values(by='Category', inplace=True, ascending=ascending)
            selected_category = st.selectbox('Filter by Category', df['Category'].unique().tolist())
            df = df[df['Category'] == selected_category]
        elif sort_selected == 'Type':
            df.sort_values(by='Type', inplace=True, ascending=ascending)
            selected_category = st.selectbox('Filter by Type', df['Type'].unique().tolist())
            df = df[df['Type'] == selected_category]

        page_df = df.copy()
        page_df.index = range(1, len(page_df) + 1)
        page_df = page_df.rename_axis('Index')
        page_df['Amount'] = page_df['Amount'].apply(lambda x: '{:.2f}'.format(x))
        st.dataframe(page_df, width=800)

        total_income = df[df['Type'] == 'Income']['Amount'].sum()
        total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
        total_overall = total_income - total_expense

        st.write(f"Total Income: ฿{total_income:.2f}  \nTotal Expense: ฿{total_expense:.2f}")
        st.write(f"Overall ฿{total_overall}")

    def aggregate_data(self, df, x_col, y_col, time_granularity):
        df[x_col] = pd.to_datetime(df[x_col])

        if time_granularity == 'Daily':
            df_aggregated = df.set_index(x_col).resample('D').sum().reset_index()
        elif time_granularity == 'Weekly':
            df_aggregated = df.set_index(x_col).resample('W-Mon').sum().reset_index()
        elif time_granularity == 'Monthly':
            df_aggregated = df.set_index(x_col).resample('M').sum().reset_index()
        elif time_granularity == 'Yearly':
            df_aggregated = df.set_index(x_col).resample('Y').sum().reset_index()
        else:
            raise ValueError("Invalid time_granularity. Use 'Daily', 'Weekly', 'Monthly', or 'Yearly'.")

        # Convert the date to a string in the format 'y-mm-dd'
        df_aggregated[x_col] = df_aggregated[x_col].dt.strftime('%Y-%m-%d')

        return df_aggregated

    def plot_bar(self, df, x_col, y_col, title, start_date, end_date, time_granularity):
        df_income = df[df['Type'] == 'Income'].groupby(x_col)[y_col].sum().reset_index()
        df_expense = df[df['Type'] == 'Expense'].groupby(x_col)[y_col].sum().reset_index()
        df_total = pd.merge(df_income, df_expense, on=x_col, how='outer', suffixes=('_Income', '_Expense')).fillna(0)

        df_filtered = df_total[(df_total[x_col] >= start_date) & (df_total[x_col] <= end_date)]
        df_filtered = df_filtered.sort_values(by=[x_col])
        min_date = df_filtered[x_col].min()
        df_filtered = df_filtered[df_filtered[x_col] >= min_date]

        df_filtered_aggregated = self.aggregate_data(df_filtered, x_col, y_col, time_granularity)
        x_label = {'Daily': 'Day', 'Weekly': 'Week', 'Monthly': 'Month', 'Yearly': 'Year'}[time_granularity]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=df_filtered_aggregated[x_col], y=df_filtered_aggregated[y_col + '_Income'], name='Total Income',
                   marker_color='green', text=df_filtered_aggregated[y_col + '_Income'], textposition='auto'))
        fig.add_trace(
            go.Bar(x=df_filtered_aggregated[x_col], y=df_filtered_aggregated[y_col + '_Expense'], name='Total Expense',
                   marker_color='red', text=df_filtered_aggregated[y_col + '_Expense'], textposition='auto'))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_label),
            yaxis=dict(title='Total Amount'),
            xaxis_type='category')

        st.plotly_chart(fig)

    def plot_line(self, df, x_col, y_col, title, start_date, end_date, time_granularity):
        df_income = df[df['Type'] == 'Income'].groupby(x_col)[y_col].sum().reset_index()
        df_expense = df[df['Type'] == 'Expense'].groupby(x_col)[y_col].sum().reset_index()
        df_total = pd.merge(df_income, df_expense, on=x_col, how='outer', suffixes=('_Income', '_Expense')).fillna(0)

        df_filtered = df_total[(df_total[x_col] >= start_date) & (df_total[x_col] <= end_date)]
        df_filtered = df_filtered.sort_values(by=[x_col])
        min_date = df_filtered[x_col].min()
        df_filtered = df_filtered[df_filtered[x_col] >= min_date]

        df_filtered_aggregated = self.aggregate_data(df_filtered, x_col, y_col, time_granularity)
        x_label = {'Daily': 'Day', 'Weekly': 'Week', 'Monthly': 'Month', 'Yearly': 'Year'}[time_granularity]

        df_filtered_aggregated['Net'] = df_filtered_aggregated[y_col + '_Income'] - df_filtered_aggregated[
            y_col + '_Expense']

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=df_filtered_aggregated[x_col], y=df_filtered_aggregated['Net'],
                       mode='lines', name='Net Income',
                       line=dict(color='white'),
                       fill='tozeroy', fillcolor='grey'
                       ))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_label),
            yaxis=dict(title='Net'),
            xaxis_type='category')

        st.plotly_chart(fig)

    def plot_waterfall(self, df, x_col, y_col, title, start_date, end_date, time_granularity):
        df_income = df[df['Type'] == 'Income'].groupby(x_col)[y_col].sum().reset_index()
        df_expense = df[df['Type'] == 'Expense'].groupby(x_col)[y_col].sum().reset_index()
        df_total = pd.merge(df_income, df_expense, on=x_col, how='outer', suffixes=('_Income', '_Expense')).fillna(0)
        df_total['Total'] = df_total[y_col + '_Income'] - df_total[y_col + '_Expense']

        df_filtered = df_total[(df_total[x_col] >= start_date) & (df_total[x_col] <= end_date)]
        df_filtered = df_filtered.sort_values(by=[x_col])
        min_date = df_filtered[x_col].min()
        df_filtered = df_filtered[df_filtered[x_col] >= min_date]

        df_filtered_aggregated = self.aggregate_data(df_filtered, x_col, y_col, time_granularity)
        x_label = {'Daily': 'Day', 'Weekly': 'Week', 'Monthly': 'Month', 'Yearly': 'Year'}[time_granularity]

        fig = go.Figure(go.Waterfall(
            name="Total",
            orientation="v",
            measure=["relative"] * len(df_filtered_aggregated),
            x=df_filtered_aggregated[x_col],
            textposition="outside",
            text=df_filtered_aggregated['Total'],
            y=df_filtered_aggregated['Total'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))

        fig.update_layout(
            title=title,
            xaxis=dict(title=x_label),
            yaxis=dict(title='Amount'),
            showlegend=True,
        )

        st.plotly_chart(fig)

    def plot_stacked(self, df, x_col, y_col, title, start_date, end_date, filter_col, filter_value):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date) & (df[filter_col] == filter_value)]
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

    def plot_pie(self, df, x_col, y_col, title, start_date, end_date, filter_col, filter_value):
        df_filtered = df[(df[x_col] >= start_date) & (df[x_col] <= end_date) & (df[filter_col] == filter_value)]
        total_amounts = df_filtered.groupby('Category')[y_col].sum()

        fig = go.Figure(data=[go.Pie(labels=total_amounts.index, values=total_amounts.values,textinfo='value', hole=0.3)])
        fig.update_layout(
            title=title,
            showlegend=True,
        )

        st.plotly_chart(fig)