#Import Libraries
from PyPDF4 import PdfFileMerger
import os,argparse

def merge_pdfs(input_files:list
              ,page_range:tuple
              ,output_file:str
              ,bookmark:bool = True
               ):
    """
    Merge a list of PDF files and save the combined result into the output_file.
    page range to select a range of pages from the input files example (0,2) -> First 2 pages / (0,6,2) -> pages 1,3,5
    add_bookmark -> add bookmarks to the output file to navigate directly to the input file section within the output file.
    """
    #strict = False -> To ignore PdfReadError - Illegal Character error
    merger = PdfFileMerger(strict=False)

    for input_file in input_files:
        bookmark_name = os.path.splitext(os.path.basename(input_file))[0] if bookmark else None

        # pages To control which pages are appended from a particular file.
        merger.append(fileobj= open(input_file,'rb')
                     ,pages=page_range
                     ,bookmark=bookmark_name
                     )

    #Insert the pdf at specific page
    merger.write(fileobj=open(output_file,'wb'))
    merger.close()


def parse_args():
    """
    Get user command line parameters
    """
    parser = argparse.ArgumentParser(description="Available Options")

    parser.add_argument( '-i'
                       , '--input_files'
                       , dest='input_files'
                       , nargs='*'
                       , type=str
                       , required=True
                       , help = "Enter the path of the files to process")

    parser.add_argument('-p'
                      , '--page_range'
                      , dest='page_range'
                      , nargs='*'
                      , help="Enter the pages to consider e.g.: (0,2) -> First 2 pages")

    parser.add_argument('-o'
                        , '--output_file'
                        , dest='output_file'
                        , required=True
                        , type=str
                        , help="Enter a valid output file")

    parser.add_argument('-b'
                        , '--bookmark'
                        , dest='bookmark'
                        , default=True
                        , type=lambda x: (str(x).lower() in ['true', '1', 'yes'])
                        , help="Bookmark resulting file")

    #To Porse The Command Line Arguments
    args = vars(parser.parse_args())

    #To Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i,j) for i,j in args.items()))
    print("######################################################################")

    return args


if __name__ == "__main__":
    # Parsing command line arguments entered by user
    args = parse_args()

    input_files = [str(x) for x in args['input_files'][0].split(',')]

    page_range = None
    if args['page_range']:
       page_range  = tuple(int(x) for x in args['page_range'][0].split(','))

    merge_pdfs( input_files = input_files
              , page_range  = page_range
              , output_file = args['output_file']
              , bookmark    = args['bookmark']
              )
