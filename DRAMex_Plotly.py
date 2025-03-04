import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import plotly.graph_objects as go

# Get a list of all CSV files that match the pattern
csv_files = glob.glob('DRAMexchange_Log/DRAMexchange_*.csv')
df_combined = pd.DataFrame()  # Initialize an empty dataframe to store combined data

# Iterate over each file and read its content
for file in csv_files:
    df = pd.read_csv(file)
    
    # Replace a specific item description with a new one
    df['Item'] = df['Item'].replace('DDR34Gb 512Mx8 1600/1866', 'DDR3 4Gb 512Mx8 1600/1866')
    
    # Extract timestamp from filename (assuming the filename format is 'DRAMexchange_YYYYMMDD_HHMM.csv')
    filename = os.path.basename(file)
    timestamp_str = filename.split('_')[1] + ' ' + filename.split('_')[2].split('.')[0]
    
    # Try to convert the extracted timestamp string into a datetime object
    try:
        timestamp = pd.to_datetime(timestamp_str, format='%Y%m%d %H%M')
    except ValueError:
        print(f"Error with the timestamp format: {timestamp_str}")
        continue
    
    # Add the timestamp as a new column in the dataframe
    df['Timestamp'] = timestamp
    
    # Concatenate the current dataframe to the combined dataframe
    df_combined = pd.concat([df_combined, df])

# Create a Plotly figure
fig = go.Figure()

# Add a trace for each unique 'Item' in the combined dataframe
for item in df_combined['Item'].unique():
    item_data = df_combined[df_combined['Item'] == item]
    fig.add_trace(go.Scatter(
        x=item_data['Timestamp'],  # X-axis: Timestamp
        y=item_data['Session Low'],  # Y-axis: Session Low value
        mode='lines',  # Display the data as a line plot
        name=item + " - Session Low"  # Set the trace label to the item name
    ))
    fig.add_trace(go.Scatter(
        x=item_data['Timestamp'],  # X-axis: Timestamp
        y=item_data['Session Average'],  # Y-axis: Session Average value
        mode='lines',  # Display the data as a line plot
        name=item + " - Session Average"  # Set the trace label to the item name
    ))

# Add annotations
avg_annotations = [dict(x=-0.05,
                         y=df_combined['Session Average'],
                         xanchor="right",
                         yanchor="bottom",
                         xref="x domain",
                         yref="y",
                         text="",
                         showarrow=False)]
low_annotations = [dict(x=-0.05,
                        y=df_combined['Session Low'],
                        xanchor="right",
                        yanchor="top",
                        xref="x domain",
                        yref="y",
                        text="",
                        showarrow=False)]

# Update layout settings such as title, axis labels, and formatting for the y-axis
fig.update_layout(
    title='Spot Trend Over Time',  # Plot title
    xaxis_title='Timestamp',  # X-axis label
    yaxis_title='Spot Price',  # Y-axis label
    legend_title='Items',  # Legend title
    yaxis=dict(
        tickprefix="$",  # Add a dollar sign before the number
        tickformat=",.2f"  # Format the y-axis values with two decimal places and thousands separator
    ),
    updatemenus=[dict(
        type="buttons",
        direction="right",
        active=0,
        x=0.57,
        y=1.2,
        buttons=[
            dict(label="All",
                 method="update",
                 args=[{"visible": [True, True, True, True]},
                       {"title": "Session Trend",
                        "annotations": low_annotations + avg_annotations}]),
            dict(label="Average",
                 method="update",
                 args=[{"visible": [False, True]},
                       {"title": "Session Average Trend",
                        "annotations": avg_annotations}]),
            dict(label="Low",
                 method="update",
                 args=[{"visible": [True, False]},
                       {"title": "Session Low Trend",
                        "annotations": low_annotations}]),
            
        ],
    )]
)

# Add a range slider for better time navigation
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([  # Add buttons for selecting different time ranges
                dict(count=1, label="1m", step="month", stepmode="backward"),  # Last 1 month
                dict(count=6, label="6m", step="month", stepmode="backward"),  # Last 6 months
                dict(count=1, label="YTD", step="year", stepmode="todate"),   # Year-to-date
                dict(count=1, label="1y", step="year", stepmode="backward"),  # Last 1 year
                dict(step="all")  # Show all data
            ])
        ),
        rangeslider=dict(
            visible=True  # Enable the range slider
        ),
        type="date"  # Set the x-axis type to date
    )
)

# Save the plot as an HTML file
fig.write_html("session_trend.html")

# Display the plot in the browser
fig.show()
