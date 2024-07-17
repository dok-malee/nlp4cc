import os
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

def download_model(model_name, save_directory):
    os.makedirs(save_directory, exist_ok=True)

    # Download and save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(save_directory)

    # Get model files
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.save_pretrained(save_directory)

    print(f"Model downloaded and saved to {save_directory}")

# Define model name and save directory
model_name = "eci-io/climategpt-7b"
save_directory = "./climategpt-7b"

# Download and save the model locally
download_model(model_name, save_directory)
