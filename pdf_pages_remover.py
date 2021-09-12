#Import libraries
import os,argparse,filetype
from PyPDF4 import PdfFileReader, PdfFileWriter

def build_range(rangeval:str):
    """
    Build the range of pages based on the parameter inputted rangeval
    """
    result=set()
    for part in rangeval.split(','):
        x=part.split('-')
        result.update(range(int(x[0]),int(x[-1])+1))
    return list(sorted(result))

def remove_pdf_pages(input_file:str
                   ,output_file:str
                   ,pages:list=None):
    """
    Remove a range of pages from a PDF file
    """
    pdf_in  = PdfFileReader(open(input_file,'rb'),strict=False)
    pdf_out = PdfFileWriter()
    try:
        for pg in range(pdf_in.getNumPages()):
            #Range of pages to remove
            if (pg+1) in pages:
               continue
            page = pdf_in.getPage(pg)
            pdf_out.addPage(page)
    except Exception as e:
        print("Exception",e)
    else:
        with open(output_file, 'wb') as pdf_output_file:
             pdf_out.write(pdf_output_file)
        pdf_output_file.close()
        pdf_in.stream.close()

def is_valid_path(path):
    """
    Validate the path inputted and make sure it is a file path of type PDF
    """
    if not path:
        raise ValueError(f"Invalid Path")
    if os.path.isfile(path) and 'pdf' in filetype.guess(path).mime:
       return path
    else:
       raise ValueError(f"Invalid Path {path}")


def parse_args():
    """
    Get user command line parameters
    """
    parser = argparse.ArgumentParser(description="Available Options")

    parser.add_argument('-i'
                       ,'--input_file'
                       ,dest='input_file'
                       ,type=is_valid_path
                       ,required=True
                       ,help = "Enter the path of the file to process")

    parser.add_argument('-o'
                      , '--output_file'
                      , dest='output_file'
                      , type=is_valid_path
                      , required=True
                      , help="Enter the path of an output file")

    parser.add_argument('-p'
                      , '--pages'
                      , dest='pages'
                      , type=str
                      , required=True
                      , help="Enter the pages to consider e.g.: 0,1 or 2-3")

    args = vars(parser.parse_args())

    #To Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i,j) for i,j in args.items()))
    print("######################################################################")

    return args


if __name__ == "__main__":
   # Parsing command line arguments entered by user
   args = parse_args()

   pages_list = build_range(args['pages'])
   remove_pdf_pages(input_file  = args['input_file']
                 , output_file = args['output_file']
                 , pages = pages_list
                  )
