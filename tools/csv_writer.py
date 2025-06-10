import csv
import os

class CsvWriter:
    """A simple wrapper for writing data to a CSV file."""
    def __init__(self, filename, fieldnames):
        """
        Initializes the writer, creating the file and writing the header.
        
        Args:
            filename (str): The full path to the CSV file.
            fieldnames (list): A list of strings for the CSV header.
        """
        self.filename = filename
        self.fieldnames = fieldnames
        
        # Ensure the directory exists
        output_dir = os.path.dirname(self.filename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Open file and write header
        self.csvfile = open(self.filename, 'w', newline='')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def writerow(self, row_dict):
        """
        Writes a single row to the CSV file.
        
        Args:
            row_dict (dict): A dictionary mapping fieldnames to values.
        """
        self.writer.writerow(row_dict)

    def close(self):
        """Closes the CSV file."""
        if self.csvfile and not self.csvfile.closed:
            self.csvfile.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 