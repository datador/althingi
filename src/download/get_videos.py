def download_meetings(first_meeting=110, max_downloads='all', max_retries=50, logging=True):
    import os
    import time
    import requests
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    from src.web.get_meetings_id import get_max_fundarnr


    print(f"Current working directory: {os.getcwd()}")
    if not os.path.exists('videos'):
        os.makedirs('videos')

    # Get logs to see what is ready if max_fundarnr is not specified
    max_fundarnr = get_max_fundarnr(logging=logging)

    # Set range for downloads based on max_downloads parameter
    if max_downloads == 'all':
        download_range = range(first_meeting, max_fundarnr+1)
    else:
        download_range = range(first_meeting, min(first_meeting + max_downloads, max_fundarnr+1))

    # Loop through the pages as described
    for i in download_range:
        url = f'https://www.althingi.is/altext/upptokur/thingfundur/?lthing=153&fundnr={i}'

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the webpage
        links = soup.find_all('a')

        # # Loop through all links and download the .mp4 files
        # for link in links:
        #     if 'Vídeóskrá með fundinum' in link.text:
        #         video_url = link['href']
        #         # Split the video URL at the last '/' to get the filename, and then split at '.' to insert the postfix before the file extension
        #         video_file_parts = video_url.split('/')[-1].split('.')
        #         video_name = os.path.join('videos', f"{video_file_parts[0]}-althingi-{i}.{video_file_parts[1]}")

        #         # Check if the file already exists and get its size
        #         if os.path.exists(video_name):
        #             downloaded_size = os.path.getsize(video_name)
        #         else:
        #             downloaded_size = 0

        for link in links:
            if 'Vídeóskrá með fundinum' in link.text:
                video_url = link['href']
                # Split the video URL at the last '/' to get the filename, and then split at '.' to insert the postfix before the file extension
                video_file_parts = video_url.split('/')[-1].split('.')
                video_name = os.path.join('videos', f"{video_file_parts[0]}-althingi-{i}.{video_file_parts[1]}")

                # Check if the file already exists and get its size
                if os.path.exists(video_name):
                    downloaded_size = os.path.getsize(video_name)

                    # Get content length from server
                    server_response = requests.head(video_url)
                    server_file_size = int(server_response.headers.get('content-length', 0))

                    if downloaded_size == server_file_size:
                        print(f"Video for meeting {i} is already downloaded.")
                        continue
                else:
                    downloaded_size = 0
                    
                retries = max_retries
                while retries > 0:
                    try:
                        headers = {'Range': f'bytes={downloaded_size}-'}  # Updated Range header

                        # Request with stream=True and the Range header
                        with requests.get(video_url, headers=headers, stream=True, timeout=None) as video_response:
                            if video_response.status_code == 416:
                                print(f"Range not satisfiable. Download for meeting {i} is complete.")
                                break
                            print(f"Response status: {video_response.status_code}, headers: {video_response.headers}")
                            video_response.raise_for_status()
                            total_size = int(video_response.headers.get('content-length', 0)) + downloaded_size
                            progress_bar = tqdm(total=total_size, initial=downloaded_size, unit='B', unit_scale=True)

                            with open(video_name, 'ab') as video_file:
                                for chunk in video_response.iter_content(chunk_size=8192):  # Increased chunk size
                                    if chunk:
                                        video_file.write(chunk)
                                        downloaded_size += len(chunk)
                                        progress_bar.update(len(chunk))

                            progress_bar.close()

                            # Verify if the file has been downloaded completely
                            if downloaded_size < total_size:
                                raise Exception("Download incomplete")

                        print(f"Downloaded video for meeting {i} to {video_name}")
                        break
                    except (requests.exceptions.RequestException, requests.exceptions.Timeout, requests.exceptions.ConnectionError, Exception) as e:  # handle network errors and timeouts and incomplete downloads
                        print(f"Download failed for meeting {i} due to {type(e).__name__}: {e}")
                        retries -= 1
                        if retries == 0:
                            print(f"Max retries reached for meeting {i}. Skipping the download.")
                        else:
                            print(f"Retrying download for meeting {i} in 2 seconds...")
                            time.sleep(2)  # Wait for 2 seconds before retrying
