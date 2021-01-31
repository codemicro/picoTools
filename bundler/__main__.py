import re
import requests
import os
import json
import zipfile 
import files

# load config file
config = None
with open("bundler.json") as f:
    config = json.load(f)

OUTPUT_DIR = "lib"
GITHUB_API = "https://api.github.com/"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for package in config:

    print("\nRunning on {}".format(package["repo"]))

    # get release info
    r = requests.get(GITHUB_API + "repos/{}/releases".format(package['repo'].replace('\\', '/')))
    r.raise_for_status()
    releases = r.json()

    # find latest compatible version
    # this assumes that GH API returns a list of releases sorted most recent last.
    release = None
    for rl in releases:
        if re.match(package["tagRegex"], rl["tag_name"]):
            release = rl
            break

    if release is None:
        print(f"No release compatible with {package['majorVersion']}.x.x for {package['repo']}")
        continue

    print("Found compatible release {}".format(release["tag_name"]))

    # find target asset
    asset_url = None
    asset_name = None
    for asset in release["assets"]:
        if re.match(package["assetNameRegex"], asset["name"]):
            print(f"Found asset {asset['name']}")
            asset_url = asset["browser_download_url"]
            asset_name = ".".join(asset["name"].split(".")[:-1])
            break

    if asset_url is None:
        print(f"No asset matching '{package['assetNameRegex']}' for {package['repo']}")
        continue

    # download target asset
    print("Downloading", asset_url)
    local = files.download_file(asset_url)

    # extract files
    with zipfile.ZipFile(local) as zf: 
        for file in package["files"]:
            
            out = os.path.join(OUTPUT_DIR, file["output"].replace("/", os.path.sep))

            dr = os.path.sep.join(out.split(os.path.sep)[:-1])
            if not os.path.exists(dr):
                os.makedirs(dr)

            src = file["source"].format(asset_name)
            print(f"Extracting {src} to {out}")
            with open(out, "wb") as out_file, zf.open(src) as src_file:
                si = src_file.read(4096)
                while si != b"":
                    out_file.write(si)
                    si = src_file.read(4096)
    
    os.remove(local)
