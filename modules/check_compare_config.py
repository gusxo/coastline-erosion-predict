if __name__ == "__main__":
    import sys

    from os.path import dirname, join, abspath
    libpath = abspath(join(dirname(__file__), "../lib"))
    sys.path.insert(0, libpath)

    from ReadConfig import ReadCompareConfig

    if len(sys.argv) < 2:
        print(f"usages : {sys.argv[0]} <config_file_path>")
        exit()
    filepath = sys.argv[1]
    is_success, msg = ReadCompareConfig(filepath)
    if is_success:
        print(f":: Read Config is Success!")
    else:
        print(f":: Read Config is Failed...\n{msg}")