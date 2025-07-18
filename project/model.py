from modelscope import snapshot_download

model_dir = snapshot_download("Qwen/Qwen3-4B", revision="master")
print("Model downloaded to:", model_dir)
