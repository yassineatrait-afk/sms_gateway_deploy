import csv

def parse_csv_numbers(file_path):
    numbers = []
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    numbers.append(row[0].strip())
    except Exception as e:
        print(f"CSV parsing error: {e}")
    return numbers
