if __name__ == "__main__":
    import os, sys
    from os.path import dirname, join, abspath
    sys.path.insert(0, abspath(join(dirname(__file__), '../lib')))
    from ReadConfig import ReadCompareConfig

    if len(sys.argv) < 2:
        print(f"usages : {sys.argv[0]} <config_file_path>")
        exit()
    filepath = sys.argv[1]
    is_success, msg = ReadCompareConfig(filepath)
    if is_success:
        print(f":: Read Config is Success!")
        print(msg)
    else:
        print(f":: Read Config is Failed...\n{msg}")