#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p models
if [ ! -f models/w600k_r50.onnx ]; then
    echo "Downloading ArcFace w600k_r50.onnx model..."
    curl -L -o models/w600k_r50.onnx https://huggingface.co/maze/faceX/resolve/e010b5098c3685fd00b22dd2aec6f37320e3d850/w600k_r50.onnx
fi

if [ ! -f models/face_detection_yunet_2023mar.onnx ]; then
    echo "Downloading YuNet face detection model..."
    curl -L -o models/face_detection_yunet_2023mar.onnx https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
fi

echo "Build successfully finished!"
