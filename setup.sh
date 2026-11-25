#!/bin/bash
# Prepara o ambiente da rotina diária (rodar a partir da raiz do repositório).
set -e
pip install --break-system-packages -q faster-whisper piper-tts pyshp scipy >/dev/null 2>&1
mkdir -p assets/piper
P=https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium
[ -f assets/piper/pt_BR-faber-medium.onnx ] || curl -sfL -o assets/piper/pt_BR-faber-medium.onnx "$P/pt_BR-faber-medium.onnx"
[ -f assets/piper/pt_BR-faber-medium.onnx.json ] || curl -sfL -o assets/piper/pt_BR-faber-medium.onnx.json "$P/pt_BR-faber-medium.onnx.json"
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')" >/dev/null 2>&1
echo "ambiente pronto"
