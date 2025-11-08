import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# Open-Meteo API (no API key required)
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_weather_data(latitude, longitude, days):
    """
    Fetch historical weather data from Open-Meteo Archive API
    """
    # Calculate date range for historical data (going backwards from today)
    end_date = datetime.now() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=days - 1)  # Going back 'days' number of days

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # API parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl",
        "timezone": "Europe/Prague",
    }

    try:
        print(
            f"Fetching historical weather data for coordinates: {latitude}, {longitude}"
        )
        print(f"Date range: {start_date_str} to {end_date_str}")
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()
        print("Historical data successfully fetched!")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def process_weather_data(raw_data):
    """
    Process raw weather data into a pandas DataFrame
    """
    if not raw_data or "hourly" not in raw_data:
        print("No valid data to process")
        return None

    hourly_data = raw_data["hourly"]

    # Create DataFrame
    df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(hourly_data["time"]),
            "temperature_celsius": hourly_data["temperature_2m"],
            "humidity_percent": hourly_data["relative_humidity_2m"],
            "precipitation_mm": hourly_data["precipitation"],
            "wind_speed_kmh": hourly_data["wind_speed_10m"],
            "pressure_hpa": hourly_data["pressure_msl"],
        }
    )

    # Add derived columns
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    df["day_name"] = df["datetime"].dt.day_name()

    print(f"Processed {len(df)} weather records")
    return df


def save_to_csv(df, filename="weather_data.csv"):
    """
    Save DataFrame to CSV file
    """
    try:
        # Save to current directory (cvicenie_L5)
        data_dir = os.path.dirname(__file__)

        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Data saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return None


def create_plotly_visualizations(df):
    """
    Create interactive visualizations using Plotly and save as one HTML file with subplots
    """
    # Save to current directory (cvicenie_L5)
    output_dir = os.path.dirname(__file__)

    # Create subplots with 2x2 grid
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Temperature Over Time",
            "Temperature vs Humidity Scatter",
            "Daily Temperature Range",
            "Weather Parameters Comparison",
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": True}],
        ],
    )

    # 1. Temperature over time (top left)
    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["temperature_celsius"],
            name="Temperature",
            line=dict(color="red"),
        ),
        row=1,
        col=1,
    )

    # 2. Temperature vs Humidity scatter plot (top right)
    fig.add_trace(
        go.Scatter(
            x=df["temperature_celsius"],
            y=df["humidity_percent"],
            mode="markers",
            name="Temp vs Humidity",
            marker=dict(
                color=df["wind_speed_kmh"],
                colorscale="Viridis",
                colorbar=dict(title="Wind Speed (km/h)", x=0.48, y=0.85, len=0.3),
                size=6,
                opacity=0.7,
            ),
        ),
        row=1,
        col=2,
    )

    # 3. Daily temperature range (bottom left)
    daily_temps = (
        df.groupby("date")["temperature_celsius"]
        .agg(["min", "max", "mean"])
        .reset_index()
    )

    fig.add_trace(
        go.Scatter(
            x=daily_temps["date"],
            y=daily_temps["max"],
            name="Max Temp",
            line=dict(color="red"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=daily_temps["date"],
            y=daily_temps["min"],
            name="Min Temp",
            fill="tonexty",
            line=dict(color="blue"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=daily_temps["date"],
            y=daily_temps["mean"],
            name="Avg Temp",
            line=dict(color="orange", width=3),
        ),
        row=2,
        col=1,
    )

    # 4. Weather parameters comparison (bottom right) - with secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["temperature_celsius"],
            name="Temperature (°C)",
            line=dict(color="red"),
        ),
        row=2,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["humidity_percent"],
            name="Humidity (%)",
            line=dict(color="blue"),
        ),
        row=2,
        col=2,
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["wind_speed_kmh"],
            name="Wind Speed (km/h)",
            line=dict(color="green"),
        ),
        row=2,
        col=2,
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title_text="Weather Data Analysis Dashboard - Historical Data",
        title_x=0.5,
        height=800,
        showlegend=True,
        legend=dict(x=1.05, y=1),
    )

    # Update x and y axis labels
    fig.update_xaxes(title_text="Date & Time", row=1, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)

    fig.update_xaxes(title_text="Temperature (°C)", row=1, col=2)
    fig.update_yaxes(title_text="Humidity (%)", row=1, col=2)

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)

    fig.update_xaxes(title_text="Date & Time", row=2, col=2)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=2)
    fig.update_yaxes(
        title_text="Humidity (%) / Wind Speed (km/h)", row=2, col=2, secondary_y=True
    )

    # Save plot as HTML file
    try:
        html_path = os.path.join(output_dir, "weather_dashboard.html")
        fig.write_html(html_path)

        print(f"Weather dashboard saved as: {html_path}")
        print("The dashboard contains 4 visualizations:")
        print("  1. Temperature Over Time")
        print("  2. Temperature vs Humidity Scatter Plot (colored by wind speed)")
        print("  3. Daily Temperature Range")
        print("  4. Weather Parameters Comparison")

    except Exception as e:
        print(f"Error saving HTML file: {e}")

    # Try to show plot (may not work in all environments)
    try:
        fig.show()
        print("Weather dashboard displayed in browser!")
    except Exception as e:
        print(f"Could not open dashboard in browser: {e}")
        print("Please open the HTML file manually to view the interactive dashboard.")

    return html_path


def main():
    """
    Main function to orchestrate the data fetching, processing, and visualization
    """
    print("=== Weather Data Analysis Tool ===")
    print("Fetching historical data from Open-Meteo Archive API...")

    # Fetch historical weather data for Košice (last 10 days)
    raw_data = fetch_weather_data(
        latitude=48.7205, longitude=21.2578, days=10
    )  # Košice

    if raw_data is None:
        print("Failed to fetch data. Exiting.")
        return

    # Process the data
    df = process_weather_data(raw_data)

    if df is None:
        print("Failed to process data. Exiting.")
        return

    # Display basic statistics
    print("\n=== Data Summary ===")
    print(f"Data points: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print("\nBasic Statistics:")
    print(df[["temperature_celsius", "humidity_percent", "wind_speed_kmh"]].describe())

    # Save to CSV
    csv_path = save_to_csv(df)

    if csv_path:
        print(f"\n=== Data saved to: {csv_path} ===")

    # Create visualizations
    print("\n=== Creating Visualizations ===")

    # Plotly visualizations (interactive)
    print("Creating interactive Plotly charts...")
    create_plotly_visualizations(df)

    print("\n=== Analysis Complete! ===")


if __name__ == "__main__":
    main()
