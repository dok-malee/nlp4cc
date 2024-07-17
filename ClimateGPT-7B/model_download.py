import os
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, cached_path, hf_bucket_url

# Function to download and save files with progress bar
def download_file(url, dest):
    if not os.path.exists(dest):
        response = cached_path(url)
        with open(dest, 'wb') as f:
            f.write(response.content)

def download_model(model_name, save_directory):
    os.makedirs(save_directory, exist_ok=True)

    # Download and save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(save_directory)

    # Get model files
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.save_pretrained(save_directory)

    # URLs for model files
    files = model.state_dict().keys()
    base_url = hf_bucket_url(model_name, filename="")

    # Download each model file with progress bar
    for file in tqdm(files, desc="Downloading model files"):
        url = base_url + file
        dest = os.path.join(save_directory, file)
        download_file(url, dest)

    print(f"Model downloaded and saved to {save_directory}")

# Define model name and save directory
model_name = "eci-io/climategpt-7b"
save_directory = "./climategpt-7b"

# Download and save the model locally
download_model(model_name, save_directory)
