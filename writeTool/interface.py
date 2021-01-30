import serial
import parse
from typing import List, Tuple


class Driver:
    lineterm = "\r".encode("UTF8")
    log = False

    def __init__(self, device="/dev/ttyACM0", baud=9600, timeout=0.5):
        self.serial = serial.Serial(device, baud, timeout=timeout)
        self.send("import os")

    def _raw_read(self) -> bytes:
        recv = self.serial.read_until(self.lineterm)
        if self.log:
            print("RECV", repr(recv))
        return recv

    def read(self) -> str:
        return self._raw_read().decode("UTF8").strip()

    def send(self, text: str):
        line = "%s\r\f" % text
        if self.log:
            print("SEND", repr(line))
        self.serial.write(line.encode("UTF8"))
        # the line should be echoed.
        # If it isn't, something is wrong.
        return text == self.read()

    def info(self) -> dict:
        self.send("os.uname()")
        return parse.uname(self.read())

    def check_traceback(self, x: str = "") -> str:
        if not x:
            x = self._raw_read().decode("UTF8").strip()
        if "traceback" in x.lower():
            return self._take_traceback()
        return ""

    def _take_traceback(self) -> str:
        line = b"Traceback (most recent call last):"
        inln = None
        while inln != b"":
            inln = self._raw_read()
            line += inln
        return line.decode("UTF8").strip("\r\n>>> ")

    def close(self):
        self.serial.close()


class FileInfo:
    name: str
    is_dir: bool
    size: int

    def __init__(self, name: str, is_dir: bool, size: int):
        self.name = name
        self.is_dir = is_dir
        self.size = size

    def __str__(self) -> str:
        return f"{self.name}: {'dir' if self.is_dir else 'file'} {self.size}"


class FileMan:
    driver: Driver

    def __init__(self, driver: Driver):
        self.driver = driver

    def list_files(self, dir: str = "") -> Tuple[List[FileInfo], str]:
        self.driver.send(f"list(os.ilistdir({repr(dir)}))")
        x = self.driver.read()
        err = self.driver.check_traceback(x)
        if err:
            return [], err
        
        dls = eval(x)
        return [
            FileInfo(x[0], x[1] == 0x4000, x[3]) for x in dls
        ], ""

    def read_file(self, filename: str) -> Tuple[str, str]:
        self.driver.send(f'open("{filename}").read()')
        ln = self.driver.read()
        err = self.driver.check_traceback(ln)
        if err:
            return "", err
        return eval(ln), ""

    def write_file(self, filename: str, content: str) -> Tuple[int, str]:
        self.driver.send(f'f = open({repr(filename)}, "w")')
        err = self.driver.check_traceback()
        if err:
            return 0, err
        self.driver.send(f"f.write({repr(content)})")
        n = self.driver.read()  # write returns number of bytes written
        self.driver.send("f.close()")
        self.driver.send("del f")
        return int(n), ""

    def delete_file(self, filename: str) -> str:
        self.driver.send(f"os.remove({repr(filename)})")
        return self.driver.check_traceback()
