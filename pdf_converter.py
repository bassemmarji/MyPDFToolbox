#Import Libraries
from pdf2docx import parse
from typing import Tuple
import os,argparse
import fitz

def convert_pdf2docx(input_file:str
                    ,output_file:str
                    ,pages:Tuple =None
                    ):
    """
    Converts pdf to docx
    """
    if pages:
       pages = [int(i) for i in list(pages) if i.isnumeric() ]

    result = parse(pdf_file=input_file
                  ,docx_with_path=output_file
                  ,pages=pages)
    summary = {
        "File":input_file
       ,"Pages":str(pages)
       ,"Output File":output_file
    }

    #Printing Summary
    print("## Summary ########################################################")
    print("\n".join("{}:{}".format(i,j) for i,j in summary.items()))
    print("###################################################################")
    return result


def convert_pdf2img(input_file:str
                   ,output_type:str
                   ,pages:Tuple =None):
    """
    Converts pdf to image and generates a file by page
    """
    #Open the document
    pdfIn = fitz.open(input_file)
    output_files = []

    #Iterate throughout the pages
    for pg in range(pdfIn.pageCount):
        if str(pages) != str(None):
           if str(pg) not in str(pages):
              continue

        #Select a page
        page = pdfIn[pg]
        rotate = int(0)

        # PDF Page is converted into a whole picture 1056*816 and then for each picture a screenshot is taken.
        # zoom = 1.33333333 -----> Image size = 1056*816
        # zoom = 2 ---> 2 * Default Resolution (text is clear, image text is hard to read)    = filesize small / Image size = 1584*1224
        # zoom = 4 ---> 4 * Default Resolution (text is clear, image text is barely readable) = filesize large
        # zoom = 8 ---> 8 * Default Resolution (text is clear, image text is readable) = filesize large
        zoom_x = 2
        zoom_y = 2
        # The zoom factor is equal to 2 in order to make text clear
        # Pre-rotate is to rotate if needed.
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)

        pix = page.getPixmap(matrix=mat, alpha=False)

        output_file = os.path.join(os.path.dirname(input_file)
                                , (os.path.splitext(os.path.basename(input_file))[0]) + '_Page' + str(pg+1) + '.' + output_type)
        pix.writePNG(output_file)

        output_files.append(output_file)
    pdfIn.close()

    summary = {
        "File":input_file
       ,"Pages":str(pages)
       ,"Output File(s)":str(output_files)
    }
    #Printing Summary
    print("## Summary ########################################################")
    print("\n".join("{}:{}".format(i,j) for i,j in summary.items()))
    print("###################################################################")

    return output_files



def convert_folder(**kwargs):
    """
    converts all PDF Files within a specified path to a selected type
    """
    input_folder            = kwargs.get('input_folder')
    #Run in recursive mode
    recursive               = kwargs.get('recursive')
    pages                   = kwargs.get('pages')
    type                    = kwargs.get('type')


    #Loop though the files within the input folder.
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            #Check if pdf file
            if not filename.endswith('.pdf'):
                continue

            #PDF File found
            inp_pdf_file = os.path.join(foldername, filename)
            print("Processing file =",inp_pdf_file)

            if type == 'docx':
               #Generate an output file
               output_file = os.path.join(
                                          os.path.dirname(inp_pdf_file)
                                        , (os.path.splitext(os.path.basename(inp_pdf_file))[0]) + '.' + type
                                         )

               convert_pdf2docx(input_file  = inp_pdf_file
                               ,output_file = output_file
                               ,pages = pages
                               )
            elif type in ('jpg','png'):
               # Generate output files
               convert_pdf2img(input_file  = inp_pdf_file
                             , output_type = type
                             , pages=pages)
        if not recursive:
           break

def is_valid_path(path):
    """
    Validates the path inputted and checks whether it is a file path or a folder path
    """
    if not path:
        raise ValueError(f"Invalid Path")
    if os.path.isfile(path):
       return path
    elif os.path.isdir(path):
       return path
    else:
       raise ValueError(f"Invalid Path {path}")


def parse_args():
    """
    Get user command line parameters
    """
    parser = argparse.ArgumentParser(description="Available Options")

    parser.add_argument('-i'
                       ,'--input_path'
                       ,dest='input_path'
                       ,type=is_valid_path
                       ,required=True
                       ,help = "Enter the path of the file or the folder to process")

    parser.add_argument('-t'
                      , '--type'
                      , dest='type'
                      , choices=['docx','jpg','png']
                      , type=str
                      , required=True
                      , help="Choose the output type")

    parser.add_argument('-p'
                      , '--pages'
                      , dest='pages'
                      , type=tuple
                      , help="Enter the pages to consider e.g.: [0,1]")

    path = parser.parse_known_args()[0].input_path
    type = parser.parse_known_args()[0].type

    if os.path.isfile(path) and type in 'docx':
          parser.add_argument('-o'
                            , '--output_file'
                            , dest='output_file'
                            , type=str
                            , required=True
                            , help="Enter a valid output file")

    if os.path.isdir(path):
       parser.add_argument('-r'
                         , '--recursive'
                         , dest='recursive'
                         , default=False
                         , type= lambda x: (str(x).lower() in ['true','1','yes'])
                         , help="Process Recursively or Non-Recursively")

    args = vars(parser.parse_args())

    #To Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i,j) for i,j in args.items()))
    print("######################################################################")

    return args

if __name__ == '__main__':
    # Parsing command line arguments entered by user
    args = parse_args()

    # If File Path
    if os.path.isfile(args['input_path']):
       if args['type'] in ('docx'):

          convert_pdf2docx(input_file  = args['input_path']
                         , output_file = args['output_file']
                         , pages = args['pages']
                          )

       elif args['type'] in ('jpg','png'):
          convert_pdf2img(input_file  = args['input_path']
                        , output_type = args['type']
                        , pages = args['pages']
                          )
    # If Folder Path
    elif os.path.isdir(args['input_path']):
        # Process a folder
        convert_folder(input_folder = args['input_path']
                      ,pages = args['pages']
                      ,type = args['type']
                      ,recursive = args['recursive']
                       )


    """
    inp_pdf_file = 'C:\\SCRIPTS\\Test\\Python Faker Library.pdf'
    #inp_pdf_file = 'C:\\SCRIPTS\\Test\\CV Bassem Marji.pdf'
    docx_file = (os.path.splitext(inp_pdf_file)[0]) + '.docx'
    #Start with page 0
    convert_pdf2docx(input_file=inp_pdf_file
                     ,output_file= docx_file
                     ,pages=[0,1,2]
                     )

    #JPG --> JPEG
    #JPEG --> JPEG
    #PNG --> PNG


    #inp_pdf_file ="C:\\SCRIPTS\\Test\\CV Bassem Marji_Eng.pdf"
    convert_pdf2img(input_file=inp_pdf_file
                  , output_folder = "C:\\SCRIPTS\\Test"
                  , output_file_type = 'PNG'
                  , pages = [1,2,3]
                   )
    """