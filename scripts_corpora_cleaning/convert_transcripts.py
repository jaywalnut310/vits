def convert_file_format(input_path, output_path):
    output_lines = []

    with open(input_path, 'r') as infile:
        for idx, line in enumerate(infile, start=1):
            # Extract the text part between quotes
            try:
                start_quote = line.index('"') + 1
                end_quote = line.rindex('"')
                text = line[start_quote:end_quote]
            except ValueError:
                continue  # Skip malformed lines

            # Format the ID: chunk_001, chunk_002, ...
            chunk_id = f"chunk_{idx:03d}"

            # Duplicate text into both the second and third columns
            formatted_line = f"{chunk_id}|{text}|{text}"
            output_lines.append(formatted_line)

    # Write the output
    with open(output_path, 'w') as outfile:
        outfile.write("\n".join(output_lines))

# Example usage
convert_file_format("cmuarctic_cut.data", "converted_ljspeech.txt")
