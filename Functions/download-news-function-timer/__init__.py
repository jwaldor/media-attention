import logging
import re
import pickle
import feedparser
import pandas as pd
#import pyodbc
import datetime
import uuid


import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    NYTURLs = []
    with open('nytrssfeedsurls.txt','rb') as nyttext:
        for line in nyttext:
    #         print(line)
            urls = re.findall('href=.*xml', str(line))
            NYTURLs+= [u.replace("href=\"","").replace('\\t',"") for u in urls]
    NYTfeeds = [feedparser.parse(url)['entries'] for url in NYTURLs]
    NYTfeeds_flat = [item for sublist in NYTfeeds for item in sublist]
    NYTfeeds_df = pd.DataFrame(NYTfeeds_flat)
    #pickle.dump(NYTfeeds_df,open('test_dump.p','wb'))

    # create a timestamp string
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # set up your blob storage connection
    connection_string = "DefaultEndpointsProtocol=https;AccountName=mediaattentionmonitor;AccountKey=sscb9YaTkNNjmEsAyPLb40Ty06jFuLYp4N/Ak70hTZ0irhHYFXT6m7E493vjZyVV2ZWY7YSPXSwl+AStvcxg5g=="
    container_name = "articles-daily-pull"
    folder_name = timestamp
    blob_name = f"{folder_name}/NYT/df_{str(uuid.uuid4())}.csv"

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

##    # create the timestamp folder if it doesn't exist
##    if not any(folder.name == folder_name for folder in container_client.list_blobs()):
##        container_client.create_blob_directory(folder_name)
##    nyt_folder_name = f"{folder_name}/NYT" # create the NYT folder if it doesn't exist
##    if not any(folder.name == nyt_folder_name for folder in container_client.list_blobs() if folder.name.startswith(folder_name)):
##        container_client.create_blob_directory(nyt_folder_name)

    # convert the DataFrame to a CSV string and upload to blob storage
    csv_string = NYTfeeds_df.to_csv(index=False)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(csv_string)
    '''
        #print('here')
    NYTURLs = []
    with open('nytrssfeedsurls.txt','rb') as nyttext:
        for line in nyttext:
    #         print(line)
            urls = re.findall('href=.*xml', str(line))
            NYTURLs+= [u.replace("href=\"","").replace('\\t',"") for u in urls]
    NYTfeeds = [feedparser.parse(url)['entries'] for url in NYTURLs]
    NYTfeeds_flat = [item for sublist in NYTfeeds for item in sublist]
    NYTfeeds_df = pd.DataFrame(NYTfeeds_flat)
    pickle.dump(NYTfeeds_df,open('test_dump.p','wb'))

    # create a timestamp string
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # set up your blob storage connection
    connection_string = "DefaultEndpointsProtocol=https;AccountName=mediaattentionmonitor;AccountKey=sscb9YaTkNNjmEsAyPLb40Ty06jFuLYp4N/Ak70hTZ0irhHYFXT6m7E493vjZyVV2ZWY7YSPXSwl+AStvcxg5g=="
    container_name = "articles-daily-pull"
    blob_name = f"df_{str(uuid.uuid4())}.csv"

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # convert the DataFrame to a CSV string and upload to blob storage
    csv_string = df.to_csv(index=False)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(csv_string)
    '''
    print(f"Saved DataFrame to blob storage with timestamp: {timestamp}")
     
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
