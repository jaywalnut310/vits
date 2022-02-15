from phonemizer import phonemize

text = "iš tiesų nežinau, ką man dabar daryti"
# text="sveiki, mano vardas yra arnas"
ph_text = phonemize(text, language='lt', backend='espeak', strip=True)

print(f"len (orig vs. phonemized): {len(text)} vs. {len(ph_text)}, text: {ph_text}")
