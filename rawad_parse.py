# Import Libraries
import fitz
import os, json, uuid
from PIL import Image
from io import BytesIO
import re

# ENCODING = 'utf8'
ENCODING = 'ascii'


def sortPageBlocks(page_blocks):
    """
    Sort the page blocks in ascending vertical order then in ascending horizontal order
    """
    blocks = []
    for b in page_blocks:
        # x coordinate in pixels
        x0 = str(int(b["bbox"][0] + 0.99999)).rjust(4, "0")
        # y coordinate in pixels
        y0 = str(int(b["bbox"][1] + 0.99999)).rjust(4, "0")
        sortage_key = y0 + x0
        blocks.append([sortage_key, b])
    blocks.sort(key=lambda x: x[0])
    # Return a list of sorted blocks
    return [b[1] for b in blocks]


def sortBlockLines(block_lines):
    """
    Sort the block lines in ascending vertical order.
    """
    lines = []
    for l in block_lines:
        y0 = str(int(l["bbox"][1] + 0.99999)).rjust(4, "0")
        lines.append([y0, l])
    lines.sort(key=lambda x: x[0])
    # Return a list of sorted lines in block
    return [l[1] for l in lines]


def sortLineSpans(line_spans):
    """
    Sort the spans of a line in an ascending horizontal direction.
    """
    spans = []
    for s in line_spans:
        x0 = str(int(s["bbox"][1] + 0.99999)).rjust(4, "0")
        spans.append([x0, s])
    spans.sort(key=lambda x: x[0])
    return [s[1] for s in spans]


def get_document_title(pdf_content):
    doc_title_bloc = -1
    doc_title = None

    for pg, page_content in pdf_content.items():
        if int(pg) == 0:
            for bloc_idx, b in page_content['Blocs'].items():
                if b['type'] == 0:
                    for line_idx, l in enumerate(sortBlockLines(b["lines"])):
                        # print(f'Page: {pg} - Bloc: {bloc_idx} - Line: {line_idx}') # - {l}
                        for span_idx, s in enumerate(sortLineSpans(l["spans"])):
                            # print(f'Span: {span_idx} - s: {s}')
                            if doc_title_bloc == -1:
                                if s['flags'] == 20 \
                                        and s['font'] == 'Arial-BoldMT':
                                    # print('Document Title=',s['text'])
                                    doc_title_bloc = bloc_idx
                                    doc_title = s['text']
                                    page_content['Blocs'][bloc_idx]['DocumentTitle'] = doc_title
    return doc_title_bloc, doc_title


def get_next_section(pdf_content, start_bloc_idx):
    section_start_bloc = -1
    section_end_bloc = -1
    section = {}

    for pg, page_content in pdf_content.items():
        for bloc_idx, b in page_content['Blocs'].items():
            # print('Block Index',bloc_idx , 'Start Bloc', start_bloc)
            if bloc_idx >= start_bloc_idx and b['type'] == 0:
                for line_idx, l in enumerate(sortBlockLines(b["lines"])):
                    # print(f'Page: {pg} - Bloc: {bloc_idx} - Line: {line_idx}') # - {l}
                    for span_idx, s in enumerate(sortLineSpans(l["spans"])):
                        if re.search('^Removal$', str(s['text']).strip()):

                            if section_start_bloc == -1:
                                section_start_bloc = bloc_idx
                                section['Header'] = s['text']
                                section['StartBloc'] = bloc_idx
                                # print('Section Header', section['Header'] , 'Start Bloc',section['StartBloc'])
                                continue

                        elif (section_start_bloc > 0 and section_end_bloc == -1
                              and re.search('^Installation$', str(s['text']).strip())):
                            section['EndBloc'] = bloc_idx
                            section['LastSection'] = 0
                            section_end_bloc = bloc_idx
                            # print('Section Header', section['Header'], 'Start Bloc',section['StartBloc'] , 'End Bloc', section['EndBloc'])
                            section_start_bloc == -1
                            return section

    section['EndBloc'] = bloc_idx
    section['LastSection'] = 1
    section_start_bloc == -1
    return section


def parse_section(pdf_content, section, output_path):
    # print('section',section)
    section_text = ""
    images = {}
    for pg, page_content in pdf_content.items():
        for bloc_idx, b in page_content['Blocs'].items():
            # print('Block Index',bloc_idx , 'Start Bloc', start_bloc)
            if section['StartBloc'] < bloc_idx < section['EndBloc']:
                # print(f'Section - {section["Header"]} - bloc {bloc_idx} - {b}')

                if b['type'] == 0:
                    # print(f'Section - {section["Header"]} - bloc {bloc_idx} - {b}')
                    for line_idx, l in enumerate(sortBlockLines(b["lines"])):
                        for s in sortLineSpans(l["spans"]):
                            # Filter spans of size < 9
                            if int(s['size']) < 9:
                                continue

                            if section_text.endswith(" ") or s["text"].startswith(" "):
                                section_text += s["text"]
                            else:
                                section_text += " " + s["text"]
                        section_text += "\n"

                if b['type'] == 1:
                    # print('Extension'  ,b['ext'])
                    # print('Image Bytes', b['image'])
                    img_stream = BytesIO(b['image'])
                    img = Image.open(img_stream).convert('RGB')
                    output_filepath = os.path.join(output_path, str(uuid.uuid4().hex) + '.png')
                    img.save(output_filepath)
                    img_stream.close()
                    images[bloc_idx] = output_filepath
                    section_text += " " + output_filepath
                    section_text += "\n"

    section["images"] = images
    section["text"] = section_text
    # print('section')
    # print(section)
    return section


################################################################################################
def parse_pdf_content(input_file: str
                      , output_path: str
                      , pages: str):
    """
    Parse PDF content
    """
    pdfIn = fitz.open(input_file)

    output_filename = os.path.join(output_path
                                   , os.path.splitext(os.path.basename(input_file))[0] + ".json")
    output_file = open(output_filename, "w", encoding=ENCODING)
    try:
        pdf_content = {}
        for pg in range(pdfIn.pageCount):
            page_content = {}
            page_content['Page'] = pg

            if pages:
                if (pg + 1) not in pages:
                    continue

            # Load the page
            page = pdfIn.loadPage(pg)
            ###################################################################
            # Extract text block dictionaries of the current page
            page_dict = page.getText("dict")

            # Loop through the arranged page blocks
            bloc_content = {}
            for bloc_idx, b in enumerate(sortPageBlocks(page_dict["blocks"])):
                bloc_index = f'{pg:03d}{bloc_idx:03d}'
                # print(f'Page {pg}, Bloc {bloc_idx}, {bloc_index} ')
                # Text Block
                if b["type"] == 0:
                    bloc_content[int(bloc_index)] = b

                # Image Block (Consider only images of width 580)
                if b["type"] == 1 and b['width'] == 580:
                    bloc_content[int(bloc_index)] = b

                page_content['Blocs'] = bloc_content

            pdf_content[str(pg)] = page_content
        # print('pdf_content')
        # print(pdf_content)
        doc_content = {}
        doc_title_bloc, doc_title = get_document_title(pdf_content)
        # print(f'Document title {doc_title} - Bloc {doc_title_bloc}')

        doc_content['title'] = doc_title
        doc_sections = {}
        install_section = {}
        if doc_title_bloc > 0:
            section = get_next_section(pdf_content, start_bloc_idx=(doc_title_bloc + 1))
            # print('Section Header', section['Header'], 'Start Bloc', section['StartBloc']
            #      , 'End Bloc',section['EndBloc'] ,'Last Section' , section['LastSection'] )

            section = parse_section(pdf_content, section, output_path)
            doc_sections['Removal'] = section
            # while True:
            # section = get_next_section(pdf_content, start_bloc_idx=section['EndBloc'])
            install_section['StartBloc'] = section['EndBloc']
            install_section['Header'] = 'Installation'
            install_section['EndBloc'] = 10000000
            install_section = parse_section(pdf_content, install_section, output_path)
            doc_sections['Installation'] = install_section

            doc_content['Sections'] = doc_sections

        print('doc_content')
        print(doc_content)

        json.dump(doc_content, output_file)
    except Exception as e:
        print("Exception", e)
    else:
        pdfIn.close()
        output_file.close()


if __name__ == '__main__':
    parse_pdf_content(input_file=".\\static\\pdfs\\2018.pdf"
                      , output_path=".\\static\\pdfs\\"
                      , pages=None
                      )
