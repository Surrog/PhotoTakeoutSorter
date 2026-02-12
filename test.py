import pytest
from byYYMM import compute_supplemental_metadata_path_suffix, compute_supplemental_metadata_path_nosuffix, keep_edited_image, base_image_path, is_edited_image, update_metadata, fetch_datetime_metadata
from pathlib import Path
from datetime import datetime

def test_compute_supplemental_metadata_path():
    path1 = Path("photo-edited.jpg")
    expected1 = Path("photo.jpg.supplemental-metadata.json")
    assert compute_supplemental_metadata_path_suffix(path1) == expected1

    path2 = Path("image-edited(1).png")
    expected2 = Path("image.png.supplemental-metadata(1).json")
    assert compute_supplemental_metadata_path_suffix(path2) == expected2

    path3 = Path("picture.jpeg")
    expected3 = Path("picture.jpeg.supplemental-metadata.json")
    assert compute_supplemental_metadata_path_suffix(path3) == expected3

    path4 = Path("snapshot(5).heic")
    expected4 = Path("snapshot.heic.supplemental-metadata(5).json")
    assert compute_supplemental_metadata_path_suffix(path4) == expected4

    path5 = Path("2021-08-08T15_36_24+02_00.JPEG")
    expected5 = Path("2021-08-08T15_36_24+02_00.JPEG.supplemental-me.json")
    assert compute_supplemental_metadata_path_suffix(path5) == expected5

    path6 = Path("IMG_20131124_115016-edited(1).jpg")
    expected6 = Path("IMG_20131124_115016.jpg.supplemental-metadata(1).json")
    assert compute_supplemental_metadata_path_suffix(path6) == expected6

    path1 = Path("photo-edited.jpg")
    expected1 = Path("photo.supplemental-metadata.json")
    assert compute_supplemental_metadata_path_nosuffix(path1) == expected1

    path2 = Path("image-edited(1).png")
    expected2 = Path("image.supplemental-metadata(1).json")
    assert compute_supplemental_metadata_path_nosuffix(path2) == expected2

    path3 = Path("picture.jpeg")
    expected3 = Path("picture.supplemental-metadata.json")
    assert compute_supplemental_metadata_path_nosuffix(path3) == expected3

    path4 = Path("snapshot(5).heic")
    expected4 = Path("snapshot.supplemental-metadata(5).json")
    assert compute_supplemental_metadata_path_nosuffix(path4) == expected4

    path5 = Path("2021-08-08T15_36_24+02_00.JPEG")
    expected5 = Path("2021-08-08T15_36_24+02_00.supplemental-metadat.json")
    assert compute_supplemental_metadata_path_nosuffix(path5) == expected5

def test_keep_edited_image():
    paths = {
        Path("photo.jpg"),
        Path("photo-edited.jpg"),
        Path("image.png"),
        Path("image-edited.png"),
        Path("picture.jpeg"),
    }

    kept_edited, deleted = keep_edited_image(paths, keep_edited=True)
    print("Kept edited:", kept_edited)
    print("Deleted:", deleted)
    assert kept_edited == {
        Path("photo-edited.jpg"),
        Path("image-edited.png"),
        Path("picture.jpeg"),
    }

    assert deleted == {
        Path("photo.jpg"),
        Path("image.png"),
    }

    kept_original, deleted = keep_edited_image(paths, keep_edited=False)
    assert kept_original == {
        Path("photo.jpg"),
        Path("image.png"),
        Path("picture.jpeg"),
    }

    assert deleted == {
        Path("photo-edited.jpg"),
        Path("image-edited.png"),
    }

    paths = {
        Path("photo.jpg"),
        Path("image.png"),
        Path("picture.jpeg"),
    }

    kept_edited, deleted = keep_edited_image(paths, keep_edited=True)
    assert kept_edited == paths
    assert deleted == set()

    kept_original, deleted = keep_edited_image(paths, keep_edited=False)
    assert kept_original == paths
    assert deleted == set()

def test_base_image_path():
    path1 = Path("photo-edited.jpg")
    base1, is_edited1 = base_image_path(path1)
    assert base1 == Path("photo.jpg")
    assert is_edited1 is True

    path2 = Path("image.png")
    base2, is_edited2 = base_image_path(path2)
    assert base2 == Path("image.png")
    assert is_edited2 is False

    path3 = Path("picture-edited(1).jpeg")
    base3, is_edited3 = base_image_path(path3)
    assert base3 == Path("picture(1).jpeg")
    assert is_edited3 is True

    path4 = Path("snapshot(5).heic")
    base4, is_edited4 = base_image_path(path4)
    assert base4 == Path("snapshot(5).heic")
    assert is_edited4 is False

def test_is_edited_image():
    assert is_edited_image(Path("photo-edited.jpg")) is True
    assert is_edited_image(Path("image.png")) is False
    assert is_edited_image(Path("picture-edited(1).jpeg")) is True
    assert is_edited_image(Path("snapshot(5).heic")) is False

def test_update_exif():
    now = datetime.now()
    update_metadata('modif.jpg', now)
    fixed = fetch_datetime_metadata('modif.jpg')
    assert now == fixed