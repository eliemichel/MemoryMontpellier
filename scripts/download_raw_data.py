from pathlib import Path
from urllib.request import urlretrieve

#---------------------------------------------

# (url, local file)
sources = [
    (
        "https://data.montpellier3m.fr/sites/default/files/ressources/MMM_MMM_ArretsTram.json",
        "MMM_MMM_ArretsTram.json",
    ),

    (
        "https://data.montpellier3m.fr/sites/default/files/ressources/MMM_MMM_LigneTram.json",
        "MMM_MMM_LigneTram.json",
    ),
]

#---------------------------------------------

def main():
    for url, local_file in sources:
        downloadDataset(url, local_file)

#---------------------------------------------

RAW_DATA_ROOT = Path(__file__).parent.parent.joinpath("data", "raw")

def downloadDataset(url, local_file):
    target_path = RAW_DATA_ROOT.joinpath(local_file)
    if not target_path.exists():
        print(f"Downloading '{url}' to '{target_path}'...")
        urlretrieve(url, target_path)

#---------------------------------------------

if __name__ == '__main__':
    main()

