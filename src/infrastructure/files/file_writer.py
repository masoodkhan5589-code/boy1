import os


class FileWriter:
    def __init__(self, file_path):
        self.file_path = file_path

    def write(self, content):
        self.ensure_file_exists()
        with open(self.file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def append(self, content):
        self.ensure_file_exists()
        with open(self.file_path, 'a', encoding='utf-8') as file:
            file.write(content)

    def ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as _:
                pass
