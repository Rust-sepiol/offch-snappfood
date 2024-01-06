import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

NUM_REQUESTS = 50
NUM_WORKERS = 5

def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' successfully removed.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found. So Creating it...")
    except PermissionError:
        print(f"Permission denied to remove file '{file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def save(text, file_handle):
    try:
        file_handle.write(text + "\n")
    except Exception as e:
        print(f"An error occurred while saving to file: {e}")

def fetch_code(
        request_number,
        CategoryCode,
        file_handle,
        session,
        CodesList,
        lock=None
    ):
    try:
        start_time = time.time()

        url = f"https://api.offch.com/coupons/{CategoryCode}/get_single_use_code"
        r = session.get(url)
        r.raise_for_status()

        code = r.text
        print(code)

        with lock:
            if code in CodesList:
                raise ValueError(
                    f"Code {code} already exists in list ! change your IP address"
                )
            CodesList.append(code)

        save(code, file_handle)



        elapsed_time = time.time() - start_time
        print(f"Request {request_number} took {elapsed_time:.2f} seconds")

    except ValueError as val_ex:
        print(f"Request {request_number} failed: {val_ex}")
        return
    except requests.HTTPError as http_ex:
        print(f"Request {request_number} failed: {http_ex}")
    except requests.RequestException as req_ex:
        print(f"Request {request_number} failed: {req_ex}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

def main():
    categories = {'Food': 1, 'Miveh': 2, 'Shirini': 3, 'Labaniat': 4, 'Attari': 5}
    CategoryCode = {1: 9191, 2: 3206, 3: 412, 4: 11169, 5: 5426}


    print("Plase Choose:")
    for category, number in categories.items():
        print(f"   {number}. {category}")


    user_choice = input("Enter the number corresponding to your choice: ")


    try:
        user_choice = int(user_choice)
        user_input = [category for category, number in categories.items() if number == user_choice][0]
    except (ValueError, IndexError):
        print("Invalid input. Please enter a valid number.")
        return

    file_path = f'code_{user_input}.txt'
    remove_file(file_path)

    CodesList = []
    lock = Lock()
    with open(file_path, "a") as file_handle, requests.Session() as session:
        args = [(i, CategoryCode[user_choice], file_handle, session, CodesList, lock) for i in range(1,NUM_REQUESTS+1)]
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            executor.map(lambda p: fetch_code(*p), args)

if __name__ == "__main__":
    main()
