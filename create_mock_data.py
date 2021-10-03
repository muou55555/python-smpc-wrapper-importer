import os
import numpy as np
import json

keys = ["age",
        "ethnicity",
        "gender",
        "heartRate",
        "nipb",
        "respiratoryRate",
        "o2saturation"]

dists = [
    np.random.randint,
    np.random.randint,
    np.random.randint,
    lambda x: np.round(np.random.normal(80, 10), 2),
    lambda x: np.round(np.random.normal(60, 10), 2),
    lambda x: np.round(np.random.normal(25, 3), 2),
    lambda x: int(np.min([np.random.normal(99, 1), 100])),
]

params = [
    5,
    3,
    2,
    0,
    0,
    0,
    0
]

offset = 2
no_patients = 100


def main():
    dataset = [{"pk": offset * no_patients + i}
               for i in range(no_patients)]
    for datum in dataset:
        schema = {}
        for idx, k in enumerate(keys):
            schema[k] = dists[idx](params[idx])
        datum["data"] = schema
    with open(os.path.join("dataset", f"full_dataset_{offset}.json"), 'w') as f:
        json.dump(dataset, f)


if __name__ == "__main__":
    main()
