
from azure.storage.fileshare import ShareServiceClient, ShareFileClient, ShareDirectoryClient
import os
from pathlib import Path


TMP_DIR = Path("/tmp")

connection_string = os.environ['AZURE_CONN_STR']
# service = ShareServiceClient.from_connection_string(conn_str=connection_string)
#
# file_client = ShareFileClient.from_connection_string(conn_str=connection_string, share_name="cceimages", file_path="my_file")
#
# parent_dir = ShareDirectoryClient.from_connection_string(conn_str=connection_string, share_name="cceimages", directory_path="images")
#
# my_list = list(parent_dir.list_directories_and_files())
#
# print(my_list)

def upload_image(source_file, fname):
    service = ShareServiceClient.from_connection_string(conn_str=connection_string)
    file_client = ShareFileClient.from_connection_string(conn_str=connection_string, share_name="cceimages", file_path="images/" + fname)
    file_client.upload_file(source_file)

def download_image(fname):
    service = ShareServiceClient.from_connection_string(conn_str=connection_string)
    file_client = ShareFileClient.from_connection_string(conn_str=connection_string, share_name="cceimages", file_path="images/" + fname)
    p = TMP_DIR / fname
    with open(p, "wb") as file_handle:
        data = file_client.download_file()
        data.readinto(file_handle)

def upload_pdf(path, fname):
    service = ShareServiceClient.from_connection_string(conn_str=connection_string)
    file_client = ShareFileClient.from_connection_string(conn_str=connection_string, share_name="cceimages", file_path="pdfs/" + fname)

    with open(path, "rb") as source_file:
        file_client.upload_file(source_file)


def download_pdf(file_path, fname):
    service = ShareServiceClient.from_connection_string(conn_str=connection_string)
    file_client = ShareFileClient.from_connection_string(conn_str=connection_string, share_name="cceimages", file_path="pdfs/" + fname)
    with open(file_path, "wb") as file_handle:
        data = file_client.download_file()
        data.readinto(file_handle)
