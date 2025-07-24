import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Load local Mistral model
model_id = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype="auto")
llm = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

# --- Prompt Functions ---

def normalize_with_llm(text):
    prompt = (
        f"[INST] Normalize the following sentence by expanding all numbers, abbreviations, and making it grammatically correct:\n"
        f"'{text}'\n"
        f"Return only the corrected sentence. [/INST]"
    )
    output = llm(prompt)[0]["generated_text"]
    return extract_response(output)

def are_equivalent(text1, text2):
    prompt = (
        f"[INST] Are these two sentences semantically equivalent?\n"
        f"Sentence A: {text1}\n"
        f"Sentence B: {text2}\n"
        f"Answer with 'Yes' or 'No' only. [/INST]"
    )
    output = llm(prompt)[0]["generated_text"]
    return "yes" in output.lower()

def extract_response(output):
    # Get only the new text after the prompt
    if "[/INST]" in output:
        return output.split("[/INST]")[-1].strip().split("\n")[0]
    return output.strip()

# --- File I/O ---

file1_path = "transcriptions.csv"
file2_path = "cmuarctic_cut.data"
output_path = "merged_output.txt"

# Load file1: chunk_id|transcription
file1_dict = {}
with open(file1_path, "r", encoding="utf-8") as f1:
    for line in f1:
        if "|" in line:
            chunk_id, transcript = line.strip().split("|", 1)
            file1_dict[chunk_id] = transcript.strip()

# Load file2: ( id "transcription" )
file2_dict = {}
with open(file2_path, "r", encoding="utf-8") as f2:
    for line in f2:
        if line.startswith("(") and '"' in line:
            parts = line.strip()[1:-1].split('"')
            if len(parts) >= 2:
                file_id = parts[0].strip()
                transcript = parts[1].strip()
                chunk_id = file_id.split("_")[-1].zfill(3)
                file2_dict[f"chunk_{chunk_id}"] = transcript

# --- Processing ---
with open(output_path, "w", encoding="utf-8") as out:
    for chunk_id in file1_dict:
        raw1 = file1_dict[chunk_id]
        raw2 = file2_dict.get(chunk_id, "")

        norm1 = normalize_with_llm(raw1)
        norm2 = normalize_with_llm(raw2) if raw2 else ""

        if norm2 and are_equivalent(norm1, norm2):
            final = norm2
        else:
            final = norm1

        out.write(f"{chunk_id}|{final}\n")
        print(f"{chunk_id} ✅")

print(f"\nDone. Output saved to: {output_path}")
