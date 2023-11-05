def load_api_keys(file_path='env.txt') -> dict:
    api_keys = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                api_keys[key] = value
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return api_keys

if __name__ == "__main__":
    api_keys = load_api_keys()  