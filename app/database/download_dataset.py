import kagglehub

# Download latest version to the default cache directory
path = kagglehub.dataset_download("anirudhsimhachalam/indian-movie-faces-datasetimfdb-face-recognition")

print("Path to dataset files:", path)
