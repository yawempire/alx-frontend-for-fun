#!/usr/bin/python3
"""Markdown to HTML"""

import sys
import os.path
import re
import hashlib

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: ./markdown2html.py README.md README.html', file=sys.stderr)
        exit(1)

    if not os.path.isfile(sys.argv[1]):
        print('Missing {}'.format(sys.argv[1]), file=sys.stderr)
        exit(1)

    with open(sys.argv[1]) as read:
        with open(sys.argv[2], 'w') as html:
            unordered_start, ordered_start, paragraph = False, False, False
            
            # Process each line from the input Markdown file
            for line in read:
                # Handle bold and italic Markdown
                line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                line = re.sub(r'__(.*?)__', r'<em>\1</em>', line)

                # Handle [[md5]] syntax
                md5_matches = re.findall(r'\[\[(.+?)\]\]', line)
                for match in md5_matches:
                    md5_hash = hashlib.md5(match.encode()).hexdigest()
                    line = line.replace(f'[[{match}]]', md5_hash)

                # Remove 'C' from ((text))
                remove_c_matches = re.findall(r'\(\((.*?)\)\)', line)
                for match in remove_c_matches:
                    cleaned_text = match.replace('C', '')
                    line = line.replace(f'(({match}))', cleaned_text)

                # Handle headings
                heading_match = re.match(r'^(#{1,6})\s*(.*)', line)
                if heading_match:
                    hashes, heading_text = heading_match.groups()
                    level = len(hashes)
                    line = f'<h{level}>{heading_text.strip()}</h{level}>\n'
                
                # Handle unordered lists
                if line.startswith('- '):
                    if not unordered_start:
                        html.write('<ul>\n')
                        unordered_start = True
                    line = f'<li>{line[2:].strip()}</li>\n'
                
                if unordered_start and not line.startswith('- '):
                    html.write('</ul>\n')
                    unordered_start = False

                # Handle ordered lists
                elif line.startswith('* '):
                    if not ordered_start:
                        html.write('<ol>\n')
                        ordered_start = True
                    line = f'<li>{line[2:].strip()}</li>\n'
                
                if ordered_start and not line.startswith('* '):
                    html.write('</ol>\n')
                    ordered_start = False

                # Handle paragraphs
                if not (heading_match or unordered_start or ordered_start):
                    if line.strip():
                        if not paragraph:
                            html.write('<p>\n')
                            paragraph = True
                        html.write(line)
                    else:
                        if paragraph:
                            html.write('</p>\n')
                            paragraph = False
                else:
                    if paragraph:
                        html.write('</p>\n')
                        paragraph = False
                    html.write(line)

            # Close any remaining open tags
            if unordered_start:
                html.write('</ul>\n')
            if ordered_start:
                html.write('</ol>\n')
            if paragraph:
                html.write('</p>\n')

    exit(0)

