class FileReader:
    def __init__(self, file_path: str):
        """
        Initialize the FileReader with the given file path.

        Args:
            file_path (str): The path to the file to be read.
        """
        self.file_path = file_path

    def read(self) -> str:
        """
        Read the entire content of the file.

        Returns:
            str: The content of the file.
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    def read_lines(self) -> list[str]:
        """
        Read the file line by line and return a list of lines.

        Returns:
            list[str]: A list of lines from the file.
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return lines
