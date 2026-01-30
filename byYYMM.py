import argparse
import os
from pathlib import Path
import json
from PIL import Image
from PIL.ExifTags import TAGS
from typing import List, Set, Dict, Tuple
from datetime import datetime
from pillow_heif import register_heif_opener

register_heif_opener()
Image.MAX_IMAGE_PIXELS = None  # Disable DecompressionBombError

image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic'}

def is_edited_image(path: Path) -> bool:
    return "-edited" in path.stem

def base_image_path(path: Path) -> Tuple[Path, bool]:
    if is_edited_image(path):
        return path.with_stem(path.stem.replace("-edited", "")), True
    return path, False

def keep_edited_image(paths: List[Path], keep_edited: bool) -> Set[Path]:
    img_to_keep: Dict[Path, Path] = {}

    for path in paths:
        base_image, is_edited = base_image_path(path)
        current = img_to_keep.get(base_image)
        if current is None:
            img_to_keep[base_image] = path
        else:
            if keep_edited and is_edited and not is_edited_image(current):
                img_to_keep[base_image] = path
            if not keep_edited and not is_edited and is_edited_image(current):
                img_to_keep[base_image] = path

    return set(img_to_keep.values())

def compute_supplemental_metadata_path_suffix(path: Path) -> Path:
    base_path, _ = base_image_path(path)
    numbered = None
    for i in range(1, 100):
        suffix = f"({i})"
        if suffix in base_path.stem:
            numbered = suffix
            base_path = base_path.with_stem(base_path.stem.replace(suffix, "")) 
            break
    updated_name_path = path.with_stem((base_path.name + ".supplemental-metadata" + (numbered if numbered else "")))
    json_path = updated_name_path.with_suffix('.json')
    json_path = json_path.with_stem(json_path.stem[:46])
    return json_path

def compute_supplemental_metadata_path_nosuffix(path: Path) -> Path:
    base_path, _ = base_image_path(path)
    numbered = None
    for i in range(1, 100):
        suffix = f"({i})"
        if suffix in base_path.stem:
            numbered = suffix
            base_path = base_path.with_stem(base_path.stem.replace(suffix, "")) 
            break
    updated_name_path = path.with_stem((base_path.stem + ".supplemental-metadata" + (numbered if numbered else "")))
    json_path = updated_name_path.with_suffix('.json')
    json_path = json_path.with_stem(json_path.stem[:46])
    return json_path


def fetch_datetime_metadata(path: Path) -> datetime:
    st = os.stat(path)
    st.st_size
    img = Image.open(path)
    metadata = img.getexif()
    for tag_id, value in metadata.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "DateTimeOriginal" or tag == "DateTime":
            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

    json_path = compute_supplemental_metadata_path_suffix(path)
    if not json_path.exists():
        json_path = compute_supplemental_metadata_path_nosuffix(path)
        
    if not json_path.exists():
        print(f"{json_path} No sidecar json found")
        raise FileNotFoundError

    with open(json_path, 'r', encoding='utf-8') as json_file:
        try:
            data = json.load(json_file)
            if 'photoTakenTime' in data:
                return datetime.fromtimestamp(int(data['photoTakenTime']['timestamp']))
            elif 'creationTime' in data:
                return datetime.fromtimestamp(int(data['creationTime']['timestamp']))
            print(f"{json_path} No DateTime found in sidecar json")
        except Exception as e:
            print(f"{json_path} Error decoding JSON: {e}")
        raise KeyError


def process_directory(directory: Path, keep_edited: bool, target: Path, dryrun: bool = False):
    img_path: List[Path] = []
    for file_path in directory.iterdir():
        if file_path.is_file():
            if file_path.suffix.lower() in image_extensions:
                img_path.append(file_path)
        if file_path.is_dir():
            process_directory(file_path, keep_edited, target)

    img_to_keep = keep_edited_image(img_path, keep_edited)

    img_metadata: Dict[Path, datetime] = {}
    for path in img_to_keep:
        img_metadata[path] = fetch_datetime_metadata(path)

    for path, dt in img_metadata.items():
        year = dt.year
        month = dt.month
        target_dir = target / f"{year:04d}/{month:02d}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / path.name
        duplicate_index = 1
        while target_path.exists():
            target_path = target_path.with_stem(f"{target_path.stem}_{duplicate_index}")
            duplicate_index += 1
        if dryrun:
            print(f"Moving {path} to {target_path}")
        else:
            path.rename(target_path)


def main():
    parser = argparse.ArgumentParser(description="Iterate through files in a directory")
    parser.add_argument("directory", type=str, help="Directory path to iterate through")
    parser.add_argument("target", type=str, help="output directory path")
    parser.add_argument("--edited", action="store_true", help="keep edited image")
    parser.add_argument("--dryrun", action="store_true", help="do not actually move files")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    target = Path(args.target)
    
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return
    
    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory")
        return
    
    print(f"Processing directory: {directory} with target: {target} and keep_edited: {args.edited}")

    process_directory(directory, args.edited, target)

if __name__ == "__main__":
    main()