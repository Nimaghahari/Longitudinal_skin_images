# Example python script for extracting tiles from Vectra JSON files
# My colleague, Adam Mothershaw, has provided this code | a.mothershaw@uq.edu.au

import pandas as pd
from pathlib import Path
import io
import base64
from PIL import Image

# Load the JSON file into a pandas dataframe
# lesions_only uses Vectra's `status` field to filter rows,
# where status==0 means "lesion for display".
def load_json(json_path, lesions_only=True):
    df = pd.DataFrame(pd.read_json(json_path)["root"]["children"])
    if lesions_only:
        df[df.status == 0].reset_index(inplace=True, drop=True)
    return(df)

# Tile images in the JSON are base64 encoded PNG. This function decodes these
# to a Pillow Image object.
def decode_tile_im(b64_data):
    decoded = base64.b64decode(b64_data)
    im = Image.open(io.BytesIO(decoded))
    return(im)

# Loads a JSON into a pandas dataframe, creates a new subdirectory named
# "[json_filename]_tiles", and saves all of the base64-encoded tiles as PNG files
# in the new directory.
# The `cc` parameter determines whether to dump the colour-corrected tiles or 
# non-colour-corrected. (colour correction is performed on a per-person basis,
# by normalising pixel values across the body).
def dump_all_images(json_path, cc=True):
    json_path = Path(json_path)
    df = load_json(json_path)
    img_col = "img64cc" if cc else "img64"
    dst_folder = json_path.parent / (json_path.stem + "_tiles")
    dst_folder.mkdir(exist_ok=True)
    df.apply(lambda row: decode_tile_im(row[img_col]).save(dst_folder / (row["uuid"] + ".png")), axis=1)

 # Modify the next line to point a folder containing JSON files
YOUR_JSON_DIRECTORY = Path("/your/json/directory")

# This will loop through all JSON files in the directory, dumping tiles for each
# one in a seperate folder.
for json_file in Path(YOUR_JSON_DIRECTORY).glob("*.json"):
    dump_all_images(json_file)
