import json
import os
import sys
import chardet
import re


class Configuration(object):
    def __init__(self):
        try:
            with open('./CharsetCheckCfg.json', 'r') as jf:
                cfg = json.load(jf)
                self.src_path = cfg['srcpath']
                self.charset = cfg['charset']
        except IOError:
            pass


class FileInfo(object):
    def __init__(self):
        self.html_files = dict()
        self.aspx_files = dict()

    def get_replace_file_paths(self, find_path):
        dirs = os.listdir(find_path)
        for i in dirs:
            sub_dir = os.path.join(find_path, i)
            if os.path.isdir(sub_dir):
                self.get_replace_file_paths(sub_dir)
            else:
                extension = os.path.splitext(i)[1].lower()
                key = sub_dir.lower()
                if extension == '.html':
                    if not self.html_files.__contains__(key):
                        self.html_files[key] = i
                elif extension == '.aspx':
                    if not self.aspx_files.__contains__(key):
                        self.aspx_files[key] = i


class FileStamptor2(object):
    def __init__(self, charset):
        self.error_logs = []
        self.charset = charset

    def load_regex(self):
        self.reg_chaset = '.*meta.+charset.*'
        self.reg_head = '.*<head.*'

    def stamp_html_files(self, source_files):
        index = 0
        length = len(source_files)
        for k in source_files:
            # self.stamp_html_file(source_files[k])
            self.stamp_html_file(k)
            index += 1
            # bar.move()
            # bar.log('The {0} file has been processed.'.format(str(index)))
            sys.stdout.flush()
            print('Process progress : {0}/{1}. File Path:{2}'.format(
                index, length, k))

    def stamp_html_file(self, source_file):
        new_lines = []
        is_modified = False
        try:
            with open(source_file, 'rb') as f:
                buf = f.read()
                code_data = chardet.detect(buf)
            with open(source_file, 'r', encoding=code_data['encoding']) as f:
                line_count = 0
                head_index = -1
                chaset_index = -1
                for line in f:
                    line_count += 1
                    if re.match(self.reg_head, line, re.M | re.I):
                        head_index = line_count
                    if re.match(self.reg_chaset, line, re.M | re.I):
                        chaset_index = line_count
                    new_lines.append(line)
            if chaset_index == -1 and head_index > -1:
                    new_lines.insert(head_index, '      <meta charset="'+self.charset+'">\n') 
                    is_modified = True
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
    print('The presetting charset:{0}'.format(config.charset))
    file_info = FileInfo()
    file_info.get_replace_file_paths(config.src_path)
    html_files = file_info.html_files
    aspx_files = file_info.aspx_files
    print('Total Html-Files count:{0}'.format(len(html_files)))
    print('Total Aspx-Files count:{0}'.format(len(aspx_files)))
    stamptor = FileStamptor2(config.charset)
    stamptor.load_regex()
    print('Begin to check charset in Html-files ...')
    stamptor.stamp_html_files(html_files)
    print('Begin to check charset in aspx-files ...')
    stamptor.stamp_html_files(aspx_files)
    print('Charset checking finished!')