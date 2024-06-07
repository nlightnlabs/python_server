import pandas as pd
import numpy as np  # Import numpy

from statsmodels.tsa.holtwinters import ExponentialSmoothing

def trend(data):
   

    df = pd.DataFrame(data)

     # Calculate max  value
    maximum = df['Value'].max()

     # Calculate min  value
    minimum = df['Value'].min()

     # Calculate sum of values
    sum = df['Value'].sum()

     # Calculate number of records
    count = df['Value'].count()

    # Calculate overall average value
    overall_average = df['Value'].mean()

    # Calculate overall median value
    overall_median = df['Value'].median()

    # Calculate standard deviation of all values
    std_dev = df['Value'].std()

    # Calculate standard deviation as a percent of overall average
    std_dev_percent = (std_dev / overall_average) * 100

    df['Value'] = df['Value'].fillna(0)

    # Calculate 25th percentile value
    percentile_25th = np.percentile(df['Value'], 25)

    # Calculate 75th percentile value
    percentile_75th = np.percentile(df['Value'], 75)

    # Calculate % change between date values
    df['% Change'] = df['Value'].pct_change()

    # Calculate average of all % change between date values
    avg_percent_change = df['% Change'].mean()

    # Calculate median of all % change between date values
    median_percent_change = df['% Change'].median()

    # Calculate total % change in the value across all dates
    total_percent_change = ((df['Value'].iloc[-1] - df['Value'].iloc[0]) / df['Value'].iloc[0]) * 100

    # Calculate moving average
    window_size = 3
    df['Moving Average'] = df['Value'].rolling(window=window_size).mean()

    # Forecasting using Exponential Smoothing with a simpler seasonal component
    model = ExponentialSmoothing(df['Value'], seasonal='multiplicative', seasonal_periods=4)
    model_fit = model.fit()
    forecast_next_value = model_fit.forecast(steps=1).iloc[0]
    forecast_3_values = model_fit.forecast(steps=3).iloc[-1]
    forecast_6_values = model_fit.forecast(steps=6).iloc[-1]
    forecast_12_values = model_fit.forecast(steps=12).iloc[-1]


    result = {
        "data": data,
        "count": count,
        "sum": sum,
        "maximum": maximum,
        "minimum": minimum,
        "overall_average":overall_average,
        "overall_median" :overall_median,
        "std_dev" : std_dev,
        "std_dev_percent":std_dev_percent,
        "percentile_25th":percentile_25th,
        "percentile_75th":percentile_75th,
        "avg_percent_change":avg_percent_change,
        "median_percent_change":median_percent_change,
        "total_percent_change":total_percent_change,
        "total_percent_change":total_percent_change,
        "window_size":window_size,
        "moving_average": df['Moving Average'].tolist(),
        "forecast_next_value":forecast_next_value,
        "forecast_3_values":forecast_3_values,
        "forecast_6_values":forecast_6_values,
        "forecast_12_values":forecast_12_values,
    }

    print(result)

    return result

data = {'Date': pd.date_range(start='2022-01-01', end='2022-12-31', freq='M'),
            'Value': [100, 120, 130, 150, 160, 180, 200, 220, 240, 250, 270, 290]}

trend(data)