import fire

from typing import List

import interface
import ports

class WriteTool:

    _driver: interface.Driver
    _fileMan: interface.FileMan
    _port: str

    def __init__(self):
        self._port = ports.get()

        print(f"Connecting on {self._port}")
        self._driver = interface.Driver(self._port)
        # self._driver.log = True
        print("Connected to", self._driver.info()["machine"])
        print()
        self._fileMan = interface.FileMan(self._driver)

    def write(self, filename: str) -> str:
        _, err = self._fileMan.write_file(filename, open(filename).read())
        if err:
            return "Unable to write file\n" + err
        else:
            return "Written"

    def ls(self, dir:str="") -> str:
        files, err = self._fileMan.list_files(dir)
        if err:
            return "Unable to list files\n" + err
        else:
            return "\n".join(files)

    def cat(self, filename: str) -> str:
        fcont, err = self._fileMan.read_file(filename)
        if err:
            return "Unable to read file\n" + err
        else:
            return fcont

    def rm(self, filename: str) -> str:
        err = self._fileMan.delete_file(filename)
        if err:
            return "Unable to delete file\n" + err
        else:
            return "Deleted"

    def rmdir(self, dirname: str) -> str:
        return "TODO"

    def wipe(self) -> str:
        return "TODO"

if __name__ == "__main__":
    fire.Fire(WriteTool)
