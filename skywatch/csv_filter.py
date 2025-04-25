
import csv

input_file = "aircraft_log_bak.csv"
output_file = "filtered.csv"
target_hex = "A842E7"

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

    writer.writeheader()

    for row in reader:
        if row.get("hex_ident") == target_hex:
            writer.writerow(row)
