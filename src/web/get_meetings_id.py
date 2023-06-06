import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_max_fundarnr(logging=False):
    # Fetch the HTML content
    url = "https://www.althingi.is/thingstorf/thingfundir-og-raedur/fundargerdir-og-upptokur/"
    response = requests.get(url)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table on the page
    table = soup.find('table')

    # Parse the table into a list of dictionaries
    data = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        data.append({
            'Fundarnúmer': cols[0].text,
            'Fundur hefst': cols[1].text,
            'Horfa': 'Horfa' in cols[1].text
        })

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data)

    # Extract number from 'Fundarnúmer' column
    df['Fundarnúmer'] = df['Fundarnúmer'].str.extract('(\d+)')[0].fillna(0).astype(int)

    # Extract start and end times from the original 'Fundur hefst' column
    df[['start_time', 'end_time']] = df['Fundur hefst'].str.extract('\((\d+:\d+) - (\d+:\d+)\)')

    # Convert 'Fundur hefst' into a datetime
    df['Fundur hefst'] = pd.to_datetime(df['Fundur hefst'].str.extract('(\d+\.\d+\.\d+)')[0], format='%d.%m.%Y')

    # Create 'ready' column
    now = datetime.now()
    df['ready'] = (df['Fundur hefst'] < now) & df['Horfa']

    # Convert to timedelta if not null
    df['start_time'] = pd.to_timedelta(df['start_time'] + ':00')
    df['end_time'] = pd.to_timedelta(df['end_time'] + ':00')

    # Calculate duration
    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60

    # Get the max 'Fundarnúmer' where 'ready' is True
    max_fundarnr = df[(df['ready'] == True)]['Fundarnúmer'].max()

    # Check if logging is True
    if logging:
        # Current timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # Filename
        filename = f'metadata_{timestamp}.csv'
        # Path
        file_path = 'logs/metadata/'

        # Ensure directory exists
        os.makedirs(file_path, exist_ok=True)

        # Save DataFrame to a CSV file
        df.to_csv(os.path.join(file_path, filename), index=False)

    return max_fundarnr
