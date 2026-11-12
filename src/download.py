"""Download and unzip CAMELS-IND v2.2 (streamflow-sufficient subset) into the Colab disk.

Nothing is stored on your laptop: the data lives only in the Colab session (/content/data).
"""
import os
import sys
import zipfile
import urllib.request

import yaml


def download(cfg_path="configs/step1.yaml"):
    cfg = yaml.safe_load(open(cfg_path))["data"]
    data_dir = cfg["data_dir"]
    os.makedirs(data_dir, exist_ok=True)
    zip_path = os.path.join(data_dir, "camels_ind.zip")

    if not os.path.exists(zip_path):
        print("Downloading CAMELS-IND (~180 MB) from Zenodo ...")
        urllib.request.urlretrieve(cfg["zenodo_url"], zip_path)
    else:
        print("Zip already present, skipping download.")

    print("Unzipping ...")
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(data_dir)
        inner = [n for n in z.namelist() if n.lower().endswith(".zip")]
    # some releases wrap zips inside the zip
    for name in inner:
        with zipfile.ZipFile(os.path.join(data_dir, name)) as z2:
            z2.extractall(data_dir)
    print("Done. Data is in", data_dir)


if __name__ == "__main__":
    download(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
