from json import JSONEncoder


class Section:
    def __init__(self, title):
        self.title = title

class SectionEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
#
# if __name__ == '__main__':
#     section = [Section('Default')]
#
#     section[0].steps = [] if not hasattr(section, 'steps') else section.steps
#     section[0].steps.append(Step(1, 'rrrr'))
#     print(section[0].steps[0])
