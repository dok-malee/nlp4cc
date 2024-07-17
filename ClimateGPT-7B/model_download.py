from transformers import AutoTokenizer, AutoModelForCausalLM

# Download and save the model locally
model_name = "eci-io/climategpt-7b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

tokenizer.save_pretrained("./climategpt-7b")
model.save_pretrained("./climategpt-7b")
