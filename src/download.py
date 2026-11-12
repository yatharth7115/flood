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
    # extract zips nested inside the release (any depth), once each
    done = set()
    while True:
        inner = [os.path.join(r, f) for r, _, fs in os.walk(data_dir) for f in fs
                 if f.lower().endswith(".zip") and os.path.join(r, f) != zip_path]
        todo = [p for p in inner if p not in done]
        if not todo:
            break
        for p in todo:
            print("  extracting nested", os.path.relpath(p, data_dir))
            with zipfile.ZipFile(p) as z2:
                z2.extractall(os.path.dirname(p))
            done.add(p)
    print("Done. Data is in", data_dir)


if __name__ == "__main__":
    download(sys.argv[1] if len(sys.argv) > 1 else "configs/step1.yaml")
