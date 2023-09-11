if __name__ == "__main__":
    import sys

    from lib.ReadConfig import ReadConfig
    from lib.InitParams import ReadAndInitParmas

    if len(sys.argv) < 2:
        print(f"usages : {sys.argv[0]} <config_file_path>")
        exit()
    filepath = sys.argv[1]
    is_success, msg = ReadConfig(filepath)
    if is_success:
        print(f":: Read Config is Success!")
        print(f":: try config-initialize...")
        is_success, msg = ReadAndInitParmas(filepath)
        if is_success:
            print(f":: Success!")
        else:
            print(f":: init Config is Failed...\n{msg}")
    else:
        print(f":: Read Config is Failed...\n{msg}")