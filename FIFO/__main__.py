from FIFO.fifo_gui import FifoGui
import argparse
from kink import di

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-dbinit")
    parser.add_argument("-demo")
    args = parser.parse_args()
    dbinit = args.dbinit
    if dbinit == "True":
        di["db_select"] = "new_db"
    else:
        di["db_select"] = "old_db"
    demo = args.demo
    if demo == "True":
        di["db_select"] = "demo_db"

    gui = FifoGui()
    gui.run()