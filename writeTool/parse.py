def uname(source: str) -> dict:
    # (sysname='rp2', nodename='rp2', release='1.13.0', version='v1.13-290-g556ae7914 on 2021-01-21 (GNU 10.2.0 MinSizeRel)', machine='Raspberry Pi Pico with RP2040')
    source = source.strip(")").strip("(")
    o = {}
    for item in source.split(", "):
        name, val = item.split("=")
        o[name] = eval(val)
    return o
