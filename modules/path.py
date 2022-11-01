if __name__ == "__main__":
    import sys
    from os.path import dirname, join, abspath
    libpath = abspath(join(dirname(__file__), "../lib"))
    sys.path.insert(0, libpath)
    print(f"python path inserted : {libpath}")
