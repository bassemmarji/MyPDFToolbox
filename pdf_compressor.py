#Import Libraries
import os,argparse
from PDFNetPython3.PDFNetPython import PDFDoc, Optimizer, SDFDoc, PDFNet

def compress_file(input_file: str,output_file:str):
    """
    Compress PDF file
    """
    if not output_file:
       output_file = input_file

    initial_size = os.path.getsize(input_file)
    try:
      # --------------------------------------------
      # Initialize the library
      PDFNet.Initialize()
      doc = PDFDoc(input_file)
      # Optimize PDF with the default settings
      doc.InitSecurityHandler()
      # Reduce PDF size by removing redundant information and compressing data streams
      Optimizer.Optimize(doc)
      doc.Save(output_file, SDFDoc.e_linearized)
      doc.Close()
      # --------------------------------------------
    except Exception as e:
      print("Error compress_file=", e)
      doc.Close()
      return False

    compressed_size = os.path.getsize(output_file)

    ratio = 1 - (compressed_size / initial_size)

    summary = {
         "Input File": input_file
       , "Initial Size": "{0:.3f} MB".format(initial_size / 1000000)
       , "Output File": output_file
       , "Compressed Size": "{0:.3f} MB".format(compressed_size / 1000000)
       , "Compression Ratio": "{0:.3%}.".format(ratio)
    }
    # Printing Summary
    print("## Summary ########################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
    print("###################################################################")

    return True


def compress_folder(**kwargs):
    """
    compress all PDF Files within a specified path
    """
    input_folder            = kwargs.get('input_folder')
    #Run in recursive mode
    recursive               = kwargs.get('recursive')

    #Loop though the files within the input folder.
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            #Check if pdf file
            if not filename.endswith('.pdf'):
                continue

            #PDF File found
            inp_pdf_file = os.path.join(foldername, filename)
            print("Processing file =",inp_pdf_file)

            #Compress Existing file
            compress_file(input_file=inp_pdf_file,output_file=None)

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

    path = parser.parse_known_args()[0].input_path

    if os.path.isfile(path):
          parser.add_argument('-o'
                            , '--output_file'
                            , dest='output_file'
                            , type=str
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

if __name__ == "__main__":
    # Parsing command line arguments entered by user
    args = parse_args()

    # If File Path
    if os.path.isfile(args['input_path']):
       compress_file(input_file=args['input_path']
                   , output_file=args['output_file']
                    )

    # If Folder Path
    elif os.path.isdir(args['input_path']):
        # Process a folder
        compress_folder(input_folder=args['input_path']
                      , recursive=args['recursive']
                       )
