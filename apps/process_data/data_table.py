from dash.dependencies import Input, Output
from dash import html, dash_table
from django_plotly_dash import DjangoDash
from .data_processing import process_uploaded_files  # Import your data processing function

# Create the Dash app using DjangoDash
app = DjangoDash(name='dash_table_app')

@app.callback(
    Output('data-table-container', 'children'),
    Input('process-button', 'n_clicks')
)
def process_and_display_data(n_clicks):
    if n_clicks is None:
        return []

    df_result = process_uploaded_files()

    data_table_columns = [{'name': col, 'id': col} for col in df_result.columns]

    df_dict = df_result.to_dict('records')

    data_table = dash_table.DataTable(
        id='data-table',
        columns=data_table_columns,
        data=df_dict,
        style_cell={'textAlign': 'left'},
        style_cell_conditional=[
            {'if': {'column_id': col_id}, 'textAlign': 'left'}
            for col_id in df_result.columns
        ]
    )

    return [data_table]


app.layout = html.Div([
    html.Button('Process Data', id='process-button'),
    html.Div(
        id='data-table-container'
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
