import os
import re
import shutil

# List of separators (you can add more here)
SEPARATORS = ['__', 'pop up']

# Root folder containing subfolders with files
MAIN_FOLDER = r'c:\main'

# Folders to exclude
EXCLUDED_FOLDERS = ['paging.py', 'output_paging', 'scripts', 'scripts-test']

# Output folder
OUTPUT_FOLDER = os.path.join(r'c:\main\output_paging')
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


def get_longest_separator(text: str) -> str:
    """
    Returns the longest separator found in the text.
    """
    longest = ''
    for sep in SEPARATORS:
        matches = re.findall(f'({re.escape(sep)}+)', text)  # Escape special chars
        if matches:
            longest = max(matches, key=len, default=longest)
    return longest


def split_text(text: str, separator: str):
    """
    Splits text by the specified separator.
    """
    return text.split(separator) if separator else [text]


def process_file(file_path: str, output_folder: str, base_folder: str):
    """
    Process the file, save the parts with the original filename and '_clean_partX'.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = text.replace('</br>', '\n')

    longest_separator = get_longest_separator(text)
    if not longest_separator:
        print(f'No valid separator found in {file_path}')
        return

    parts = split_text(text, longest_separator)
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    output_subfolder = os.path.join(output_folder, f'{base_folder}_clean')
    os.makedirs(output_subfolder, exist_ok=True)

    for i, part in enumerate(parts[1:], start=1):  # Skip the first part (parts[0])
        cleaned = part.strip()
        low = cleaned.lower()
        if not cleaned or 'invalid' in low or 'completed' in low:
            continue

        output_file_name = f'{base_name}_clean_part{i}.log'
        output_file_path = os.path.join(output_subfolder, output_file_name)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)

    print(f'Parts saved in {output_subfolder} with the base name {base_name}')


def process_all_files():
    """
    Processes all files in all subdirectories under MAIN_FOLDER.
    """
    for root, dirs, files in os.walk(MAIN_FOLDER):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]
        for filename in files:
            base_folder_name = os.path.basename(root)
            file_path = os.path.join(root, filename)
            process_file(file_path, OUTPUT_FOLDER, base_folder_name)


if __name__ == '__main__':
    process_all_files()
