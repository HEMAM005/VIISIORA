import os
import random
import shutil

# Original dataset folder
dataset_dir = "D:\House_Room_Dataset"

# New split dataset folder
output_dir = "dataset/rooms"

split_ratio = (0.7, 0.2, 0.1)

for category in os.listdir(dataset_dir):

    category_path = os.path.join(dataset_dir, category)

    if not os.path.isdir(category_path):
        continue

    images = os.listdir(category_path)
    random.shuffle(images)

    train_split = int(len(images) * split_ratio[0])
    val_split = int(len(images) * split_ratio[1])

    train_images = images[:train_split]
    val_images = images[train_split:train_split + val_split]
    test_images = images[train_split + val_split:]

    for split, split_images in zip(
        ["train", "val", "test"],
        [train_images, val_images, test_images]
    ):

        split_folder = os.path.join(output_dir, split, category)
        os.makedirs(split_folder, exist_ok=True)

        for img in split_images:
            src = os.path.join(category_path, img)
            dst = os.path.join(split_folder, img)
            shutil.copy(src, dst)

print("Dataset split completed.")