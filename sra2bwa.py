"""
Usage:
    sra-bwa.py --fastq FILE

Options:
    -h, --help          Show this message.

    -f, --fastq FILE    Input FASTQ file.

"""

from docopt import docopt
import sys
import os
import gzip

args = docopt(__doc__, version='1.0')

input_file = args['--fastq']

base_name = input_file[input_file.rfind('/')+1:input_file.rfind('.') if input_file.rfind('.') != -1 else None]
l_ext = base_name.split('.')[-1].lower()
if l_ext == 'fastq' or l_ext == 'fq':
    base_name = base_name[:base_name.rfind('.')]
output_file = base_name + '.bwa.fastq'

class myGzipFile(gzip.GzipFile):
    def __enter__(self, *args, **kwargs):
        if self.fileobj is None:
            raise ValueError("I/O operation on closed GzipFile object")
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

def sniff(path):
    with open(path, 'rb') as f:
        gz = f.read(2) == '\x1f\x8b'
    opn = myGzipFile if gz else open
    with opn(path) as f:
        first_line = f.readline().rstrip()
        if first_line.split(" ")[0].endswith(".1") or first_line.split(" ")[0].endswith(".2"):
            return True
        else:
            return False

def ReadnameFixFastq(filename, new_file):

    with open(filename, 'rb') as f: #check if input is gzipped
        gz = f.read(2) == '\x1f\x8b'
    opn = myGzipFile if gz else open
    fh = opn(filename, 'r')
    new_fh = open(new_file, 'w')
    while True:
        readname = fh.readline().rstrip()  # read name line
        if len(readname) == 0:
            break
        pos = readname.split(' ')[0].rfind('.')
        readname = list(readname)
        readname[pos] = "/"
        new_fh.write("".join(readname)+"\n") # write changed readname
        new_fh.write(fh.readline())  # copy base sequence
        new_fh.write(fh.readline())  # copy placeholder line
        new_fh.write(fh.readline())  # copy quality line
    fh.close()
    new_fh.close()


with open(input_file, 'rb') as f:  # check if input is gzipped
    gz = f.read(2) == '\x1f\x8b'
if gz:
    suffix = '.gz'
else:
    suffix = ''
    
if sniff(input_file):
    ReadnameFixFastq(input_file, output_file)
    sys.stderr.write('Fastq file fixed to work in BWA alignment')
else:
    os.rename(input_file, output_file + suffix)
    sys.stderr.write('Fastq file not changed')
