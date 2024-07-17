from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate import load_checkpoint_and_dispatch
import torch
import os

# Ensure the current device is mps if available
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

# Create an offload folder
offload_folder = "./offload_folder"
os.makedirs(offload_folder, exist_ok=True)

# Load tokenizer from local directory
tokenizer = AutoTokenizer.from_pretrained("./climategpt-7b")

# Load model from local directory
model = AutoModelForCausalLM.from_pretrained("./climategpt-7b")

# Dispatch model to device with offloading
model = load_checkpoint_and_dispatch(
    model,
    "./climategpt-7b",
    device_map="auto",
    offload_folder=offload_folder
)

# Generate text
input_text = "What are the effects of climate change?"
input_ids = tokenizer(input_text, return_tensors='pt').input_ids.to(device)

outputs = model.generate(input_ids, max_length=200, num_return_sequences=1)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
