from huggingface_hub import hf_hub_download
import os

def download_model():
    """
    Download the GGUF model from Hugging Face Hub and store it locally.
    Environment Variables:
        HF_REPO_ID (str): Hugging Face repository ID.
        HF_FILENAME (str): Model filename to download.
        HF_LOCAL_DIR (str): Local directory to store the model.
    """
    repo_id = os.getenv("HF_REPO_ID")
    filename = os.getenv("HF_FILENAME")
    local_dir = os.getenv("HF_LOCAL_DIR")

    if not repo_id or not filename or not local_dir:
        raise RuntimeError("HF_REPO_ID, HF_FILENAME, and HF_LOCAL_DIR must be set")

    model_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir
    )

    print("Model downloaded at:", model_path)
    return model_path

if __name__ == "__main__":
    download_model()
