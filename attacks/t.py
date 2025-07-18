import os

def read_file_to_array(file_path):
    # Expand the ~ to the full path
    expanded_path = os.path.expanduser(file_path)
    
    try:
        with open(expanded_path, 'r', encoding='latin-1') as file:  # Using 'latin-1' encoding
            lines = file.readlines()
        return [line.strip() for line in lines]
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# Example usage
file_path = "~/wordlists/rockyou.txt"
wordlist = read_file_to_array(file_path)
print(wordlist)
