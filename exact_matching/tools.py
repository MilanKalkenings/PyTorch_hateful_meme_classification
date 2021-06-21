import pandas as pd
import torch
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from torch.utils.data import Dataset
from PIL import Image


def select_device():
    """
    Tries to detect a Cuda-GPU.
    Detects the CPU if no GPU available.

    :return: the name of the detected device.
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()  # clean GPU
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    return device


def evaluate(y_true, y_probas):
    """
    Evaluates the prediction-probabilities of a model
    using accuracy_score, f1_score, precision, and recall

    :param torch.Tensor y_true: true labels
    :param torch.Tensor y_probas: predicted class probabilities
    :return: dict, a dictionary having the keys "acc", and "f1" and the respective values.
    """
    preds_batch_np = np.round(y_probas.cpu().detach().numpy())
    y_batch_np = y_true.cpu().detach().numpy()
    acc = accuracy_score(y_true=y_batch_np, y_pred=preds_batch_np)
    f1 = f1_score(y_true=y_batch_np, y_pred=preds_batch_np, zero_division=0)
    precision = precision_score(y_true=y_batch_np, y_pred=preds_batch_np, zero_division=1)
    recall = recall_score(y_true=y_batch_np, y_pred=preds_batch_np, zero_division=1)
    return {"acc": acc, "f1": f1, "precision": precision, "recall": recall}


class CustomDataset(Dataset):
    """
    A custom Image Dataset that performs transformations on the images contained in it and shifts them to
    a given device.
    """

    def __init__(self, data, transform_pipe, x_name="img", y_name="detected", device="cuda"):
        """
        Constructor.

        :param pd.DataFrame data: A DataFrame containing one column of image paths and another columns of image labels.
        :param transform_pipe: a transform:Composition of all transformations that have to be applied to the images
        :param str x_name: name of the image column
        :param str y_name: name of the label column
        :param str device: name of the device that has to be used
        """
        self.data = data
        self.transform_pipe = transform_pipe
        self.x_name = x_name
        self.y_name = y_name
        self.device = device

    def __len__(self):
        """
        Returns the number of observations in the whole dataset

        :return: the length of the dataset
        """
        return len(self.data)

    def __getitem__(self, i):
        """
        Is used by DataLoaders to draw the observation at index i in the dataset.

        :param int i: index of an observation
        :return: a list containing the image-data and the label of one observation
        """
        img_path = "../../data/hateful_memes_data/" + self.data[self.x_name].iloc[i]
        x = self.transform_pipe(Image.open(img_path, formats=["PNG"])).to(self.device)
        if x.size(0) == 4:  # very few images have one more channel, change to RGB format
            image = Image.open(img_path, formats=["PNG"]).convert("RGB")
            x = self.transform_pipe(image).to(self.device)
        y = torch.tensor(self.data[self.y_name][i], dtype=torch.float).to(self.device)
        return [x, y]

def read_data(detected_share, data_path="../../data/exact_matching/"):
    """
    Reads the exact matching data.

    :param float detected_share: determines the amount of detected hateful memes in the data.
    :param str data_path: directory in which the data is stored.
    :return: a dictionary containing the sets train, val, test, detected and non-detected.
    """
    train = pd.read_csv(data_path + "exact_train_" + str(detected_share) + ".csv")
    val = pd.read_csv(data_path + "exact_val_" + str(detected_share) + ".csv")
    test = pd.read_csv(data_path + "exact_test_" + str(detected_share) + ".csv")

    detected = pd.read_csv(data_path + "exact_detected_" + str(detected_share) + ".csv")
    non_detected = pd.read_csv(data_path + "exact_non_detected_" + str(detected_share) + ".csv")
    return {"train": train, "val": val, "test": test, "detected": detected, "non_detected": non_detected}