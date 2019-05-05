import os
import sys
import re
import fnmatch
import argparse
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.formatters.html import DOC_HEADER
from pygments.formatters.html import DOC_FOOTER

def parse_args():
    parser = argparse.ArgumentParser(description='A tool to collect codes and highlight syntax in a single html document.')
    parser.add_argument('sources', metavar='source', nargs='+', type=str, help='source code directory or file', default='.')
    parser.add_argument('-o', '--out',  help='output file path. default is output.html', default='output.html', dest='output')
    parser.add_argument('-i', '--ignore', help='path of the ignore file, similar to .gitignore. default is ignore.txt', default='ignore.txt', dest='ignore_file')
    parser.add_argument('-f', '--footer', help='file footer string, you can use </br> to insert lines. default is </br>', default='</br>', dest='file_footer')
    args = parser.parse_args()

    sources = []
    for s in args.sources:
        s = os.path.expanduser(s).rstrip(os.path.sep)
        if os.path.exists(s):
            sources.append(s)
        else:
            print('error: "', s, '" does not exists!', sep='')
    if len(sources) != len(args.sources):
        return None
    args.sources = sources
    
    args.output = os.path.expanduser(args.output)

    args.ignore_file = os.path.expanduser(args.ignore_file)
    args.ignore_patterns = parse_ignore_file(args.ignore_file)

    return args

def parse_ignore_file(path):
    if not os.path.exists(path):
        print('warning: no ignore file specified, all codes will be collected')
        return []
    try:
        with open(path, 'r') as fd:
            ss = fd.readlines()
            ss = [s.strip('\n') for s in ss if len(s.strip('\n')) > 0]
            return ss
    except:
        return []

def main(args):
    with open(args.output, 'w') as write_fd:
        hf = HtmlFormatter()
        write_fd.write(header(hf))
        for path in args.sources:
            collect_files(path, write_fd, hf, args.ignore_patterns, args.file_footer)
        write_fd.write(footer())

def split_path_components(base_path, file_path):
    components = []
    p = file_path
    while True:
        if p == base_path or len(p) == 0:
            break
        p, f = os.path.split(p)
        components.append(f)
    return components

def should_ignore_file(base_path, file_path, ignore_patterns):
    components = split_path_components(base_path, file_path)
    for name in components:
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
    return False
    
def highlight_and_write_file(full_path, write_fd, hf, footer):
    try:
        with open(full_path) as fd:
            content = fd.read()
            lexer = get_lexer_for_filename(full_path, code=content)
            formatted = highlight(content, lexer, hf)
            write_fd.write(formatted)
            write_fd.write(footer)
            print('"', full_path, '" highlighted with ', short_class_name(lexer), ' has been written to "', write_fd.name, '"', sep='')
    except:
        pass # eat all exceptions

def collect_files(path, write_fd, hf, ignore_patterns, footer):
    subfiles = os.listdir(path)
    subfiles.sort()
    for subfile in subfiles:
        if subfile.startswith('.'):
            continue
        full_path = os.path.join(path, subfile)
        if should_ignore_file(path, subfile, ignore_patterns):
            print('ignore "', full_path, '"', sep='')
            continue
        if os.path.isdir(full_path):
            collect_files(full_path, write_fd, hf, ignore_patterns, footer)
        else:
            highlight_and_write_file(full_path, write_fd, hf, footer)

def header(hf):
    return DOC_HEADER % dict(
        title=hf.title, 
        styledefs=hf.get_style_defs('body'), 
        encoding=hf.encoding)

def footer():
    return DOC_FOOTER

def short_class_name(obj):
    t = type(obj)
    m = re.match(r'<class \'(\w+\.)*(\w+)\'>', str(t))
    return m.group(2)

if __name__ == "__main__":
    args = parse_args()
    if args is not None:
        main(args)
    # split_path_components('/Users', '/Users/jjwang/abcdefg.h')