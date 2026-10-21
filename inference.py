"""Offline inference for the accompanying leaf image classifier."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from safetensors.torch import load_file
import timm
import torch
from torchvision import transforms


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_classifier(model_dir):
    root = Path(model_dir)
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    weights = root / config["weights_file"]
    labels_path = root / config["labels_file"]
    if _sha256(weights) != config["weights_sha256"]:
        raise ValueError("Model file checksum mismatch")
    if _sha256(labels_path) != config["labels_sha256"]:
        raise ValueError("Label mapping checksum mismatch")
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    if set(labels) != {str(i) for i in range(config["num_classes"])}:
        raise ValueError("Label mapping does not match the classifier")
    model = timm.create_model(config["architecture"], pretrained=False,
                              num_classes=config["num_classes"])
    model.load_state_dict(load_file(str(weights), device="cpu"), strict=True)
    model.eval()
    preprocessing = config["preprocessing"]
    pipeline = transforms.Compose([
        transforms.Resize(tuple(preprocessing["input_size"]),
                          interpolation=transforms.InterpolationMode.BILINEAR,
                          antialias=preprocessing["antialias"]),
        transforms.ToTensor(),
        transforms.Normalize(preprocessing["mean"], preprocessing["std"]),
    ])
    return model, pipeline, labels, config


def predict_image(image, classifier):
    model, pipeline, labels, config = classifier
    inputs = pipeline(image.convert("RGB")).unsqueeze(0)
    with torch.inference_mode():
        logits = model(inputs)
        probabilities = torch.softmax(logits / config["decision"]["softmax_temperature"], dim=1)
        best_score, best_index = torch.max(probabilities[0], dim=0)
        scores, indices = probabilities[0].topk(min(3, config["num_classes"]))
    class_id = int(best_index)
    score = float(best_score)
    accepted = (class_id != config["decision"]["reject_class_id"]
                and score >= config["decision"]["confidence_threshold"])
    return {"class_id": class_id, "label": labels[str(class_id)], "score": score,
            "accepted": accepted, "top3": [
                {"class_id": int(index), "label": labels[str(int(index))], "score": float(value)}
                for value, index in zip(scores, indices)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--model-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    torch.set_num_threads(2)
    classifier = load_classifier(args.model_dir)
    with Image.open(args.image) as image:
        result = predict_image(image, classifier)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
