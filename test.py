import pytest
from byYYMM import compute_supplemental_metadata_path_suffix, compute_supplemental_metadata_path_nosuffix
from pathlib import Path

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