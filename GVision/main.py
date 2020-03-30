from __future__ import unicode_literals
from __future__ import print_function
import sys
from time import sleep
from gooey import Gooey, GooeyParser
import DataLoader as dl


@Gooey(progress_regex=r"^progress: (-?\d+)%$",
       disable_progress_bar_animation=True)
def main():
    parser = GooeyParser(prog="example_progress_bar_1")
    parser.add_argument('FolderChooser', help="name of the file to process", widget='DirChooser') 
    parser.add_argument('FolderDist', help="name of the file to process", widget='DirChooser') 
    args = parser.parse_args(sys.argv[1:])

    # Loading directory data
    dl.start(args.FolderChooser, args.FolderDist)

if __name__ == "__main__":
    sys.exit(main())
