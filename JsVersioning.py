# encoding: utf-8-sig
'''
author: JiaKai
This is a script to replace the JS-File version of the target HTML-Files
parameters: -r(--root): static files root
            -e(--edition): static files edition
            -pre(--prefix): static server path
            -suf(--suffix): suffixes to be versioned
            -src(--srcpath): static files folder path
            -dst(--dstpath): replace files folder path
            -t(--stamptype): stamp type: time or hash or none(not to stamp)
            -f(--forced): versioned include no '?t=xxx' flag
            -d(--detail): show the versiong process
            -src(--log): True-replace logged
'''

import os
import shutil
import time
import re
import datetime
import argparse
import chardet
import sys
import json
import hashlib


class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1

    def log(self, s):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        print(s)
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('#' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()


class Configuration(object):
    def __init__(self):
        try:
            with open('./VersionCfg.json', 'r') as jf:
                cfg = json.load(jf)
                self.root = cfg['root']
                self.edition = cfg['edition']
                self.prefix = cfg['prefix']
                self.suffixes = cfg['suffix'].split(';')
                self.src_path = cfg['srcpath']
                self.dst_path = cfg['dstpath']
                self.stamp_type = cfg['stamptype']
                self.is_forced = self.str2bool(cfg['forced'])
                self.is_detailed = self.str2bool(cfg['detailed'])
                self.is_logged = self.str2bool(cfg['logged'])
        except IOError:
            pass

    def str2bool(self, s):
        return str(s).lower() in ('true', 'yes', 'y', 't', '1')


class FileMapper(object):
    def __init__(self, stamp_type, root, edition):
        self.files = dict()
        self.stamp_type = stamp_type
        self.root = root
        self.edition = edition

    # get file md5 hash
    def get_file_md5(self, file_name):
        if not os.path.isfile(file_name):
            return ""
        myhash = hashlib.md5()
        try:
            with open(file_name, 'rb') as f:
                while True:
                    b = f.read(8096)
                    if not b:
                        break
                    myhash.update(b)
            return myhash.hexdigest()
        except IOError:
            return ""

    # timestamp -> time string
    def TimeStampToTime(self, timestamp):
        timeStruct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

    # Get the file modify time & modify time string
    def get_file_modifytime(self, file_path):
        # file_path = unicode(file_path, 'utf8')
        t = os.path.getmtime(file_path)
        tstr = self.TimeStampToTime(t)
        return int(t), tstr

    def get_file_stamps(self, file_path, suffix):
        dirs = os.listdir(file_path)
        root_len = len(self.root)
        for i in dirs:
            if i == self.edition:
                continue
            sub_dir = os.path.join(file_path, i).lower()
            if os.path.isdir(sub_dir):
                self.get_file_stamps(sub_dir, suffix)
            else:
                if os.path.splitext(i)[1].lower() == "." + suffix.lower():
                    root_index = sub_dir.find(self.root)
                    if root_index > -1:
                        latest_dir = file_path[:root_index+root_len] + '\\' + self.edition + file_path[root_index+root_len:]
                        # relative_dir = sub_dir[root_index:]
                        relative_dir = os.path.join(latest_dir, i).lower()
                        relative_key = relative_dir[root_index:]
                        if not os.path.exists(latest_dir):
                            os.makedirs(latest_dir)
                        if not os.path.exists(relative_dir):
                            shutil.copy2(sub_dir, latest_dir)
                        if not self.files.__contains__(relative_key):
                            if self.stamp_type.lower() == 'none':
                                fstamp = ''
                            elif self.stamp_type == 'hash':
                                fstamp = self.get_file_md5(relative_dir)
                            else:
                                fstamp, _ = self.get_file_modifytime(relative_dir)
                            self.files[relative_key] = fstamp

    def write_stamps(self):
        try:
            with open('./VersionMap.json', 'w') as jf:
                jf.write(json.dumps(self.files))
        except IOError:
            pass


# Deprecated
class JsInfo():
    def __init__(self):
        self.js_files = dict()

    # timestamp -> time string
    def TimeStampToTime(self, timestamp):
        timeStruct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

    # Get the file modify time & modify time string
    def get_file_modifytime(self, file_path):
        # file_path = unicode(file_path, 'utf8')
        t = os.path.getmtime(file_path)
        tstr = self.TimeStampToTime(t)
        return t, tstr

    def get_js_filenames(self, find_path):
        dirs = os.listdir(find_path)
        for i in dirs:
            sub_dir = os.path.join(find_path, i)
            if os.path.isdir(sub_dir):
                self.get_js_filenames(sub_dir)
            else:
                if os.path.splitext(i)[1].lower() == '.js':
                    if not self.js_files.__contains__(i):
                        t, tstr = self.get_file_modifytime(sub_dir)
                        self.js_files[i] = {'stamp': t, 'time': tstr}


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
                '''
                if extension == '.html':
                    if not self.html_files.__contains__(i):
                        self.html_files[i] = sub_dir
                elif extension == '.aspx':
                    if not self.aspx_files.__contains__(i):
                        self.aspx_files[i] = sub_dir
                '''
                key = sub_dir.lower()
                if extension == '.html':
                    if not self.html_files.__contains__(key):
                        self.html_files[key] = i
                elif extension == '.aspx':
                    if not self.aspx_files.__contains__(key):
                        self.aspx_files[key] = i


# 1.初始化对象
# 2.加载json中的文件版本号
# 3.使用目标后缀生成正则
# 4.更新文件版本信息
class FileStamptor2(object):
    def __init__(self, forced, detailed, static_path, root, edition):
        self.replace_logs = {}
        self.error_logs = []
        self.forced = forced
        self.detailed = detailed
        self.static_path = static_path
        self.static_paths = re.split('[\\/]+', static_path)
        self.root = root
        self.edition = edition

    def load_regex(self, suffix):
        if suffix == 'css':
            self.reg_html_link = '.*href=["\'](.+\.' + suffix + ')\?t=(\w+)["\']'
            self.reg_html_link_f = '.*href=["\'](.+\.' + suffix + ')["\']'
        else:
            self.reg_html_link = '.*src=["\'](.+\.' + suffix + ')\?t=(\w+)["\']'
            self.reg_html_link_f = '.*src=["\'](.+\.' + suffix + ')["\']'

    def load_stamps(self):
        try:
            with open('./VersionMap.json', 'r') as jf:
                self.stamp_dict = json.load(jf)
        except IOError:
            pass

    def stamp_html_files(self, source_files):
        index = 0
        length = len(source_files)
        # bar = ProgressBar(total=length, width=length)
        for k in source_files:
            # self.stamp_html_file(source_files[k])
            self.stamp_html_file(k)
            index += 1
            # bar.move()
            # bar.log('The {0} file has been processed.'.format(str(index)))
            sys.stdout.flush()
            if self.detailed:
                print('Process progress : {0}/{1}. File Path:{2}'.format(
                    index, length, k))
            else:
                print(
                    'Process progress : {0}/{1}. File Path:{2}'.format(
                        index, length, k),
                    end='\r')

    '''
    # 生成文件在静态服务器的路径
    # 1.获取文件相对深度depth
    # 2.获取文件绝对路径absolute_path
    # 3.用静态路径(static_path)加上绝对路径中逆向相对深度的路径
    # 4.获取完整的静态路径
    def get_static_file_path(self, static_path, relative_path, absolute_path):
        relative_paths = re.split('[\\/]+', relative_path)
        # absolute_paths = re.split('[\\/]+', absolute_path)
        absolute_paths = absolute_path.split('\\')
        if relative_paths[0] == '.':
            depth = len(relative_paths) - 1
        else:
            depth = len(relative_paths)
        path = '/'.join(absolute_paths[len(absolute_paths):])
        return static_path.rstrip('\\/') + '/' + path
    '''

    def get_static_file_path(self, static_path, root, absolute_path):
        abs_paths = re.split('[\\/]+', absolute_path)
        if len(abs_paths) < 2:
            abs_paths = re.split(r'\\', absolute_path)
        if abs_paths[0] == root:
            abs_paths = abs_paths[1:]
        abs_path = '/'.join(abs_paths)
        return static_path.rstrip('\\/') + '/' + abs_path

    def stamp_html_file(self, source_file):
        new_lines = []
        is_modified = False
        html_path = os.path.dirname(source_file)
        root_len = len(self.root)
        static_len = len(self.static_path)
        try:
            with open(source_file, 'rb') as f:
                buf = f.read()
                code_data = chardet.detect(buf)
            with open(source_file, 'r', encoding=code_data['encoding']) as f:
                line_count = 0
                for line in f:
                    line_count += 1
                    # line = line.replace(self.static_path, '')
                    m = re.match(self.reg_html_link, line, re.M | re.I)
                    if m:
                        # file_paths = re.split('[\\/]+', m.group(1))
                        # file_name = file_paths[len(file_paths) - 1]
                        if m.group(1).startswith(self.static_path):
                            root_index = html_path.find(self.root)
                            m_paths = m.group(1)[static_len:].lstrip('/').split('/')
                            m_path = '\\'.join(m_paths)
                            file_name = html_path[:root_index+root_len] + '\\' + m_path
                        else:
                            file_name = os.path.abspath(
                                os.path.join(html_path, m.group(1))).lower()
                        root_index = file_name.find(self.root)
                        if root_index > -1:
                            if file_name.find(self.edition) > 0:
                                file_name = file_name[root_index:root_index+root_len] + file_name[root_index+root_len:]
                            else:
                                file_name = file_name[root_index:root_index+root_len] + '\\' + self.edition + file_name[root_index+root_len:]
                            # file_name = file_name[root_index:]
                        if self.stamp_dict.__contains__(file_name):
                            # Add static prefix
                            '''
                            if self.static_path and not m.group(1).startswith(self.static_path):
                                sp = self.get_static_file_path(self.static_path, m.group(1), file_name)
                                line = line.replace(m.group(1), sp)
                                is_modified = True
                            '''
                            # Update version stamp
                            file_stamp = self.stamp_dict[file_name]
                            if file_stamp and file_stamp != m.group(2):
                                # js_stamp = int(js_info['stamp'])
                                # if int(m.group(2)) < js_stamp:
                                new_lines.append(
                                    line.replace(m.group(2), str(file_stamp)))
                                is_modified = True
                                if not self.replace_logs.__contains__(
                                        source_file):
                                    self.replace_logs[source_file] = []
                                self.replace_logs[source_file].append(
                                    'Line: %d' % line_count)
                                # else:
                                #     new_lines.append(line)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    elif self.forced:
                        fm = re.match(self.reg_html_link_f, line, re.M | re.I)
                        if fm:
                            # file_paths = re.split('[\\/]+', fm.group(1))
                            # file_name = file_paths[len(file_paths) - 1]
                            if fm.group(1).startswith(self.static_path):
                                edition_index = fm.group(1).find(self.edition)
                                paths = fm.group(1)[edition_index+len(self.edition)+1:].split('/')
                                file_name = self.root + '\\' + '\\'.join(paths)
                            else:
                                file_name = os.path.abspath(
                                    os.path.join(html_path, fm.group(1))).lower()
                            root_index = file_name.find(self.root)
                            if root_index > -1:
                                file_name = file_name[root_index:root_index+root_len] + '\\' + self.edition + file_name[root_index+root_len:]
                                # file_name = file_name[root_index:]
                            if self.stamp_dict.__contains__(file_name):
                                # Add static prefix
                                '''
                                if self.static_path and not fm.group(1).startswith(self.static_path):
                                    sp = self.get_static_file_path(self.static_path, fm.group(1), file_name)
                                    line = line.replace(fm.group(1), sp)
                                    is_modified = True
                                '''
                                # Add version stamp
                                # if self.stamp_dict.__contains__(source_file):
                                file_stamp = self.stamp_dict[file_name]
                                if file_stamp:
                                    f_index = line.find(fm.group(1))
                                    new_line = line[:f_index] \
                                        + line[f_index:f_index+len(fm.group(1))] \
                                        + '?t=' + file_stamp \
                                        + line[f_index+len(fm.group(1)):]
                                    # new_line = line[:f_index] + '?t=' + file_stamp + line[f_index:]
                                    if self.static_path and not fm.group(1).startswith(self.static_path):
                                        sp = self.get_static_file_path(self.static_path, self.root, file_name)
                                        new_line = new_line.replace(fm.group(1), sp)
                                    new_lines.append(new_line)
                                    is_modified = True
                                    if not self.replace_logs.__contains__(
                                            source_file):
                                        self.replace_logs[source_file] = []
                                    self.replace_logs[source_file].append(
                                        'Line: %d' % line_count)
                                else:
                                    new_line = line
                                    if self.static_path and not fm.group(1).startswith(self.static_path):
                                        sp = self.get_static_file_path(self.static_path, self.root, file_name)
                                        new_line = new_line.replace(fm.group(1), sp)
                                    new_lines.append(new_line)
                                    is_modified = True
                                    if not self.replace_logs.__contains__(
                                            source_file):
                                        self.replace_logs[source_file] = []
                                    self.replace_logs[source_file].append(
                                        'Line: %d' % line_count)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
        # except UnicodeDecodeError:
        # except (TypeError, UnicodeDecodeError, IOError):
        except Exception as exp:
            self.error_logs.append("{0} replace failed!\nException:{1}".format(
                source_file, str(exp)))
        if is_modified:
            with open(source_file, 'w', encoding='utf-8-sig') as f:
                for line in new_lines:
                    f.write(line)

    def write_replace_logs(self):
        path = os.getcwd() + '\\replace_log_' + datetime.datetime.now(
        ).strftime('%Y%m%d%H%M%S') + ".log"
        with open(path, 'w', encoding='utf-8-sig') as f:
            for k in self.replace_logs:
                f.write('%s:%s\n\n' % (k, self.replace_logs[k]))
        if len(self.error_logs) > 0:
            path = os.getcwd() + '\\replace_error_log_' + datetime.datetime.now(
            ).strftime('%Y%m%d%H%M%S') + ".log"
            with open(path, 'w', encoding='utf-8-sig') as f:
                for k in self.error_logs:
                    f.write('%s\n' % (k))


# Deprecated
class FileStamptor():
    def __init__(self):
        self.reg_html_js = '.*src=["\'](.+\.js)\?t=(\w+)["\']'
        self.reg_html_js_f = '.*src=["\'](.+\.js)["\']'
        self.reg_aspx_js = '\"(\w+\.js)\?t=(\w+)\"'
        self.replace_logs = dict()
        self.error_logs = []

    def load_stamps(self):
        try:
            with open('./VersionMap.json', 'r') as jf:
                self.stamp_dict = json.load(jf)
        except IOError:
            pass

    def stamp_html_files(self, source_files, show_detail):
        index = 0
        length = len(source_files)
        # bar = ProgressBar(total=length, width=length)
        for k in source_files:
            self.stamp_html_file(source_files[k])
            index += 1
            # bar.move()
            # bar.log('The {0} file has been processed.'.format(str(index)))
            sys.stdout.flush()
            if show_detail:
                print('Process progress : {0}/{1}. File Path:{2}'.format(
                    index, length, source_files[k]))
            else:
                print(
                    'Process progress : {0}/{1}. File Path:{2}'.format(
                        index, length, source_files[k]),
                    end='\r')

    def stamp_html_file(self, source_file):
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
                    m = re.match(self.reg_html_js, line, re.M | re.I)
                    if m:
                        js_paths = re.split('[\\/]+', m.group(1))
                        js_name = js_paths[len(js_paths) - 1]
                        if self.stamp_dict.__contains__(js_name):
                            js_info = self.stamp_dict[js_name]
                            if js_info:
                                js_stamp = int(js_info['stamp'])
                                # if int(m.group(2)) < js_stamp:
                                new_lines.append(
                                    line.replace(m.group(2), str(js_stamp)))
                                is_modified = True
                                if not self.replace_logs.__contains__(
                                        source_file):
                                    self.replace_logs[source_file] = []
                                self.replace_logs[source_file].append(
                                    'Line: %d' % line_count)
                                # else:
                                #     new_lines.append(line)
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
        # except UnicodeDecodeError:
        # except (TypeError, UnicodeDecodeError, IOError):
        except Exception:
            self.error_logs.append("{0} replace failed!\n".format(source_file))
        if is_modified:
            with open(source_file, 'w', encoding='utf-8-sig') as f:
                for line in new_lines:
                    f.write(line)

    def write_replace_logs(self):
        path = os.getcwd() + '\\replace_log_' + datetime.datetime.now(
        ).strftime('%Y%m%d%H%M%S') + ".log"
        with open(path, 'w', encoding='utf-8-sig') as f:
            for k in self.replace_logs:
                f.write('%s:%s\n\n' % (k, self.replace_logs[k]))
        if len(self.error_logs) > 0:
            path = os.getcwd() + '\\replace_error_log_' + datetime.datetime.now(
            ).strftime('%Y%m%d%H%M%S') + ".log"
            with open(path, 'w', encoding='utf-8-sig') as f:
                for k in self.error_logs:
                    f.write('%s\n' % (k))


if __name__ == '__main__':
    # Init configuration from cfg.json
    config = Configuration()
    # configuration from command-line
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', help='static files root')
    parser.add_argument('-e', '--edition', help='static files edition')
    parser.add_argument('-pre', '--prefix', help='static server path')
    parser.add_argument('-suf', '--suffix', help='suffixes to be versioned')
    parser.add_argument('-src', '--srcpath', help='static files folder path')
    parser.add_argument('-dst', '--dstpath', help='replace files folder path')
    parser.add_argument('-t', '--stamptype', help='stamp type: time or hash')
    parser.add_argument(
        '-f', '--forced', help="versioned include no '?t=xxx' flag")
    parser.add_argument('-d', '--detail', help="show the versiong process")
    parser.add_argument('-l', '--log', help="True-replace logged")
    args = parser.parse_args()
    if args.root:
        config.root = args.root
    if args.edition:
        config.edition = args.edition
    if args.prefix:
        config.prefix = args.prefix
    if args.suffix:
        config.suffixes = args.suffix.split(';')
    if args.srcpath:
        config.src_path = args.srcpath
    if args.dstpath:
        config.dst_path = args.dstpath
    elif config.src_path:
        config.dst_path = config.src_path
    if args.stamptype:
        config.stamp_type = args.stamptype
    if args.forced:
        config.is_forced = config.str2bool(args.forced)
    if args.detail:
        config.is_detailed = config.str2bool(args.detail)
    if args.log:
        config.is_logged = config.str2bool(args.log)
    print('The src-Files path:{0}'.format(config.src_path))
    print('The dst-Files path:{0}'.format(config.dst_path))
    # get static file stamps and write to json dictionary
    file_mapper = FileMapper(config.stamp_type, config.root, config.edition)
    for suf in config.suffixes:
        file_mapper.get_file_stamps(config.src_path, suf)
    file_mapper.write_stamps()
    # Get the html&aspx files that need to be stamped
    file_info = FileInfo()
    file_info.get_replace_file_paths(config.src_path)
    html_files = file_info.html_files
    aspx_files = file_info.aspx_files
    print('Total Html-Files count:{0}'.format(len(html_files)))
    print('Total Aspx-Files count:{0}'.format(len(aspx_files)))
    # Stamping
    stamptor = FileStamptor2(config.is_forced, config.is_detailed,
                             config.prefix, config.root, config.edition)
    stamptor.load_stamps()
    for suf in config.suffixes:
        stamptor.load_regex(suf)
        print('Begin to version {0} stamps in Html-files ...'.format(suf))
        stamptor.stamp_html_files(html_files)
        print('Begin to version {0} stamps in Aspx-files ...'.format(suf))
        stamptor.stamp_html_files(aspx_files)
        print('{0} files stamps ended!'.format(suf))
    if config.is_logged:
        stamptor.write_replace_logs()
    print(
        'Files version updated successfully, the log file was created successfully.'
    )
    '''
    # Get the js stamps
    js_info = JsInfo()
    js_info.get_js_filenames(src_path)
    js_stamps = js_info.js_files
    print('Total JS-Files count:{0}\n'.format(len(js_stamps)))
    # Get the html&aspx files that need to be stamped
    file_info = FileInfo()
    file_info.get_replace_file_paths(hp)
    html_files = file_info.html_files
    aspx_files = file_info.aspx_files
    print('Total Html-Files count:{0}\n'.format(len(html_files)))
    # Stamping
    stamptor = FileStamptor()
    stamptor.stamp_html_files(html_files, js_stamps, show_detail)
    stamptor.write_replace_logs()
    print(
        'Html-Files version updated successfully, the log file was created successfully.'
    )
    '''
