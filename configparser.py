class IrregualrConfigParser(object):

    COMMENT_FLAGS = ("#", ";")
    def __init__(self):
        super(IrregualrConfigParser, self).__init__()
        self.__content = []

    def read(self, fn_or_fp):
        content = []
        if isinstance(fn_or_fp, file):
            content = [line.strip() for line in fn_or_fp.xreadlines()]
        else:
            with open(fn_or_fp, "r") as fp:
                content = [line.strip() for line in fp.xreadlines()]

        self.__content = self.parse_content(content)

    def write(self, fp):
        for line in self.__content:
            if line is None:
                fp.write("\n")
                continue

            section = line.get("section", None)
            comment = line.get("comment", None)
            option = line.get("option", None)
            value = line.get("value", None)
            if comment:
                fp.write(comment + "\n")
                continue
            elif section and option is None:
                fp.write("[{0}]\n".format(section))
                continue
            elif option and value is not None:
                fp.write("{0}={1}\n".format(option, value))
            elif not section and not option:
                continue
            else:
                fp.write(option + "\n")

    def parse_content(self, content):
        def _parse_content():
            section = None
            for line in content:
                if not line:
                    yield None
                    continue

                if line[0] in self.COMMENT_FLAGS:
                    yield {"comment": line}
                    continue

                if line[0] == '[' and line[-1] == ']':
                    section = line[1:-1]
                    yield {"section": section}
                    continue

                if "=" in line:
                    option, value = [i.strip() for i in line.split("=", 1)]
                    yield {"option": option, "value": value, "section": section}
                else:
                    yield {"option": line, "section": section}

        if not content:
            return []
        else:
            return list(_parse_content())

    def __get_option(self, section, option):
        for ln, line in enumerate(self.__content):
            if not line:
                continue

            section_name = line.get("section", None)
            option_name = line.get("option", None)
            if section_name == section and option_name == option:
                return ln, line

        return -1, None

    def __get_section(self, section):
        for ln, line in enumerate(self.__content):
            if not line:
                continue

            section_name = line.get("section", None)
            if section_name == section:
                return ln, line

        return -1, None

    def has_section(self, section):
        ln, _ = self.__get_section(section)
        return ln != -1

    def has_option(self, section, option):
        ln, _ = self.__get_option(section, option)
        return ln != -1

    def __add_section(self, section):
        line = {"section": section}
        self.__content.append(line)
        return len(self.__content) - 1, line

    def add_section(self, section):
        ln, _ = self.__add_section(section)
        return ln != -1

    def get(self, section, option):
        _, option_line = self.__get_option(section, option)
        if not option_line:
            return None
        else:
            return option_line.get("value", None)

    def set(self, section, option, value=None):
        _, option_line = self.__get_option(section, option)
        if option_line:
            if value is None:
                option_line.pop('value', None)
            else:
                option_line['value'] = value
            return True

        ln, _ = self.__get_section(section)
        if ln == -1:
            ln, _ = self.__add_section(section)

        if value is None:
            line = {"option": option, "section": section}
        else:
            line = {"option": option, "value": value, "section": section}
        self.__content.insert(ln + 1, line)
        return True
