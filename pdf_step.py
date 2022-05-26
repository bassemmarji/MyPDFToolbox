import re
import json
from pymongo import MongoClient
from pdf_section import Section, SectionEncoder
from read_json import get_pdf_json


class Step:
    def __init__(self, number, title):
        self.title = title
        self.number = number


def get_section(all_lines: str):
    sections = []
    steps = []
    index = 0
    is_prev_section = False
    step_index = 0
    sub_steps = []
    descriptions = []
    if all_lines is None or len(all_lines.strip()) == 0:
        pass
    sections.append(Section('Default'))
    all_lines = all_lines.split('\n')
    for line in all_lines:
        line = line.strip()
        # print(line)
        if bool(re.match("^\\d+$", line)):
            continue
        if re.search('pdfs', line):
            section = sections[len(sections)] if len(sections) < 1 else sections[len(sections) - 1]
            step = section.steps[step_index - 1]
            step = step.sub_steps[len(sub_steps) - 1] if hasattr(step, 'sub_steps') and len(
                step.sub_steps) > 0 else step
            step.images = [] if not hasattr(step, 'images') else step.images
            step.images.append(line)
        elif " " in line:
            line = line.strip()

            line_number = int(line[0:line.index(" ")])
            line_txt = line[line.index(" ") + 1:].strip()

            step_number = line_txt[0:line_txt.index(".")] if bool(re.match("^\\d+", line_txt)) else ""

            if line_number < 50:
                if is_prev_section:
                    sections[len(sections) - 1].title += "\n" + line_txt
                else:
                    sections.append(Section(line_txt))
                index += 1
                step_index = 0
                is_prev_section = True

            elif 93 < line_number < 105:
                section = sections[len(sections)] if len(sections) < 1 else sections[len(sections) - 1]
                step = section.steps[step_index - 1]
                if hasattr(step, 'sub_steps') and len(step.sub_steps) > 0:
                    step = step.sub_steps[len(sub_steps) - 1]
                if not line_txt.strip()[0].isupper():
                    step.title = step.title + "\n" + line_txt if hasattr(step, 'title') else "\n" + line_txt
                else:
                    step.descriptions = [] if not hasattr(step, 'descriptions') else step.descriptions
                    step.descriptions.append(line_txt)
                is_prev_section = False
            elif 69 < line_number < 79:

                section = sections[len(sections) - 1] if len(sections) > 1 else sections[0]
                step = section.steps[step_index - 1]
                step = step.sub_steps[len(step.sub_steps) - 1] if hasattr(step, 'sub_steps') else step

                step.title = step.title + "\n" + line_txt if hasattr(step, 'title') else line_txt
            elif 50 < line_number < 61:
                step_index += 1
                section = sections[len(sections) - 1] if len(sections) > 1 else sections[0]
                section.steps = [] if not hasattr(section, 'steps') else section.steps
                section.steps.append(Step(step_number, line_txt))
                is_prev_section = False
            elif 80 < line_number < 95:
                section = sections[len(sections) - 1] if len(sections) > 1 else sections[0]
                step = section.steps[step_index - 1]
                step.sub_steps = [] if not hasattr(step, 'sub_steps') else step.sub_steps
                step.sub_steps.append(Step(step_number, line_txt))
                is_prev_section = False
    return sections


def parse_json_doc(json_content):
    document = {}

    for key, value in json_content.items():
        sections = get_section(value) if value and len(value.strip()) > 0 else None
        document[key] = sections
        if sections:
            if not hasattr(sections[0], 'steps'):
                del sections[0]

            print(json.dumps(sections, indent=4, cls=SectionEncoder))


# if __name__ == '__main__':
#     parse_json_doc()
