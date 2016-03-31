import csv
import io
import os

from time import time

import reverse_geocoder as rg

# source file without reverse-geocoded values
src_file_path = '/home/data/quake-info/catsearch.5055'
src_delimiter = ','
src_quotechar = '"'
src_quoting = csv.QUOTE_MINIMAL

# target file with reverse-gencoded values
tgt_file_path = os.path.splitext(src_file_path)[0] + '_reverse_geocoded.csv'
tgt_delimiter = ','
tgt_quotechar = '"'
tgt_quoting = csv.QUOTE_MINIMAL

max_rows = 0 # how many rows to process, 0 means unlimited
flush_rows = 10000 # how many rows to flush to output at a time

# beginning time hack
bgn_time = time()

# initialize
# row counters
row_count = 0
out_count = 0

# if the source file exists
if os.path.exists(src_file_path):

    # open the target file for writing
    with io.open(tgt_file_path, 'w', newline='') as tgt_file:

        # open the source file for reading
        with io.open(src_file_path, 'r', newline='') as src_file:

            # open a CSV file dictionary reader object
            csv_reader = csv.DictReader(src_file, delimiter=src_delimiter, quoting=src_quoting)

            # obtain the field names from
            # the first line of the source file
            fieldnames = csv_reader.fieldnames
            # append the reverse geo-coding
            # result fields to field names list
            fieldnames.append('cc')
            fieldnames.append('admin1')
            fieldnames.append('admin2')
            fieldnames.append('name')

            # instantiate the CSV dictionary writer object with the modified field names list
            csv_writer = csv.DictWriter(tgt_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)

            # output the header row
            csv_writer.writeheader()

            # beginning time hack
            bgn_time = time()

            # reader row-by-row
            for row in csv_reader:

                row_count += 1

                # convert string lat/lon
                # to floating-point values
                latitude = float(row['Latitude'])
                longitude = float(row['Longitude'])

                # instantiate coordinates tuple
                coordinates = (latitude, longitude)

                # search for the coordinates
                # returning the cc, admin1, admin2, and name values
                # using a mode 1 (single-threaded) search
                results = rg.search(coordinates, mode=1) # default mode = 2

                # if results obtained
                if results is not None:
                    # result-by-result
                    for result in results:
                        # map result values
                        # to the row values
                        row['cc'] = result['cc']
                        row['admin1'] = result['admin1']
                        row['admin2'] = result['admin2']
                        row['name'] = result['name']
                        # output a row
                        csv_writer.writerow(row)
                        out_count += 1
                else:
                    # map empty values
                    # to the row values
                    row['cc'] = ''
                    row['admin1'] = ''
                    row['admin2'] = ''
                    row['name'] = ''
                    # output a row
                    csv_writer.writerow(row)
                    out_count += 1

                # if row count equals or exceeds max rows
                if max_rows > 0 and row_count >= max_rows:
                    # break out of reading loop
                    break

                # if row count is modulus
                # of the flush count value
                if row_count % flush_rows == 0:

                    # flush accumulated
                    # rows to target file
                    tgt_file.flush()

                    # ending time hack
                    end_time = time()
                    # compute records/second
                    seconds = end_time - bgn_time
                    if seconds > 0:
                        rcds_per_second = row_count / seconds
                    else:
                        rcds_per_second = 0
                    # output progress message
                    message = "Processed: {:,} rows in {:,.0f} seconds @ {:,.0f} records/second".format(row_count, seconds, rcds_per_second)
                    print(message)

# ending time hack
end_time = time()
# compute records/second
seconds = end_time - bgn_time
if seconds > 0:
    rcds_per_second = row_count / seconds
else:
    rcds_per_second = row_count
# output end-of-processing messages
message = "Processed: {:,} rows in {:,.0f} seconds @ {:,.0f} records/second".format(row_count, seconds, rcds_per_second)
print(message)
print("Processing finished, %d rows output!" % out_count)

