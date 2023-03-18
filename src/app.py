
import dash
import yfinance as yf
import random
from dash import dcc, html, Input, Output, State
from plotly import graph_objects as go


app = dash.Dash(__name__)
server = app.server
# this function makes a game where you guess if candles go up od down

app.layout = html.Div([
    html.H1('Game: Up or Down over next 10 candles?'),
    dcc.Graph(id='candle-chart'),
    html.Div([
        html.Button('Up', id='yes-button'),
        html.Button('Down', id='no-button'),
        html.Button('New Game', id='new-game-button')
    ]),
    html.Div(id='outcome-text')
])

correct_guesses = 0
total_guesses = 0
opacity_current = 1
fig = None
stock_data = yf.download('GOOG', start='2011-01-01', end='2021-12-31')
start_index = random.randint(0, len(stock_data) - 50)
end_index = start_index + 50
 
# Define a callback function that updates the chart and outcome text based on user input
@app.callback(
    [Output('outcome-text', 'children'), Output('candle-chart', 'figure')],
    [Input('new-game-button', 'n_clicks'), 
     Input('yes-button', 'n_clicks'), 
     Input('no-button', 'n_clicks')]
)
def update_game(reset_clicks, yes_clicks, no_clicks):
    global correct_guesses, total_guesses, opacity_current, stock_data, fig, start_index, end_index

    guess = None
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'new-game-button':
        start_index = random.randint(0, len(stock_data) - 50)
        end_index = start_index + 50
        opacity_current = 1
    
    if button_id == 'yes-button':
        guess = 'up'
        opacity_current = 0.3

    if button_id == 'no-button':
        guess = 'down'
        opacity_current = 0.3

    if guess is not None:
        close = round(stock_data['Close'][end_index - 11],2)
        final = round(stock_data['Close'][end_index-1],2)

        if (final > close and guess == 'up') or (final < close and guess == 'down'):
            outcome_text = f'Correct {close} to {final}'
            correct_guesses += 1
        else:
            outcome_text = f'Incorrect {close} to {final}.'
        total_guesses += 1
    else: 
        outcome_text = 'Click Up or Down'
    
    success_rate = 100 if total_guesses == 0 else round(correct_guesses / total_guesses * 100)
    outcome_text += f' You made {total_guesses} guesses, success rate {success_rate}%.'

    fig = go.Figure(data=[go.Candlestick(
        x=stock_data.index[start_index:end_index],
        open=stock_data['Open'][start_index:end_index],
        high=stock_data['High'][start_index:end_index],
        low=stock_data['Low'][start_index:end_index],
        close=stock_data['Close'][start_index:end_index])])
    fig.update_layout(
        title=f'Candlestick Chart for GOOG',
        xaxis_title='Date',
        yaxis_title='Price')
    fig.update_xaxes(rangeslider_visible=False)

    close = stock_data['Close'][end_index - 11]
    max_diff_total = max(stock_data['High'][start_index:end_index]) - close
    min_diff_total = close - min(stock_data['Low'][start_index:end_index])
    delta = max(max_diff_total, min_diff_total)
    fig.update_yaxes(range=[close-delta, close+delta])

    fig.add_shape(
        type="rect",
        x0=stock_data.index[end_index - 10],
        y0=close-delta,
        x1=stock_data.index[end_index - 1],
        y1=close+delta,
        line=dict(color="white", width=14.2),
        fillcolor="white",
        opacity=opacity_current,
        layer="above"
    )

    return outcome_text, fig


if __name__ == '__main__':
    app.run_server(debug=True)

