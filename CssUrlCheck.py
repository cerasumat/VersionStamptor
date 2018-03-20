import json
import os
import sys
import chardet
import re


class Configuration(object):
    def __init__(self):
        try:
            with open('./CssUrlCfg.json', 'r') as jf:
                cfg = json.load(jf)
                self.src_path = cfg['srcpath']
        except IOError:
            pass


class FileInfo(object):
    def __init__(self):
        self.css_files = dict()

    def get_replace_file_paths(self, find_path):
        dirs = os.listdir(find_path)
        for i in dirs:
            sub_dir = os.path.join(find_path, i)
            if os.path.isdir(sub_dir):
                self.get_replace_file_paths(sub_dir)
            else:
                extension = os.path.splitext(i)[1].lower()
                key = sub_dir.lower()
                if extension == '.css':
                    if not self.css_files.__contains__(key):
                        self.css_files[key] = i


class FileStamptor2(object):
    def __init__(self):
        self.error_logs = []

    def load_regex(self):
        self.reg_url = '.*url\((\S+)\).*'

    def stamp_css_files(self, source_files):
        index = 0
        length = len(source_files)
        for k in source_files:
            # self.stamp_html_file(source_files[k])
            self.stamp_css_file(k)
            index += 1
            # bar.move()
            # bar.log('The {0} file has been processed.'.format(str(index)))
            sys.stdout.flush()
            print('Process progress : {0}/{1}. File Path:{2}'.format(
                index, length, k))

    def stamp_css_file(self, source_file):
        new_lines = []
        is_modified = False
        try:
            with open(source_file, 'rb') as f:
                buf = f.read()
                code_data = chardet.detect(buf)
            with open(source_file, 'r', encoding=code_data['encoding']) as f:
                line_count = 0
                for line in f:
                    line_count += 1
                    m = re.match(self.reg_url, line, re.M | re.I)
                    if m:
                        path_index = line.index(m.group(1))
                        if path_index > -1:
                            new_line = line[:path_index] + m.group(1).lower() + line[path_index+len(m.group(1)):]
                            new_lines.append(new_line)
                            is_modified = True
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
        except Exception as exp:
            self.error_logs.append("{0} replace failed!\nException:{1}".format(
                source_file, str(exp)))
        if is_modified:
            with open(source_file, 'w', encoding='utf-8-sig') as f:
                for line in new_lines:
                    f.write(line)
   

if __name__ == '__main__':
    config = Configuration()
    print('The src-Files path:{0}'.format(config.src_path))
    file_info = FileInfo()
    file_info.get_replace_file_paths(config.src_path)
    css_files = file_info.css_files
    print('Total Css-Files count:{0}'.format(len(css_files)))
    stamptor = FileStamptor2()
    stamptor.load_regex()
    print('Begin to check charset in Css-files ...')
    stamptor.stamp_css_files(css_files)

