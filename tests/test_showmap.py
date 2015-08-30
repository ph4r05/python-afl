# encoding=UTF-8

# Copyright © 2015 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import subprocess as ipc
import sys
import tempfile

from nose.tools import (
    assert_equal,
    assert_not_equal,
)

here = os.path.dirname(__file__)
target = os.path.join(here, 'target.py')

def run(cmd, stdin='', expected_exit_status=0):
    child = ipc.Popen(
        list(cmd),
        stdin=ipc.PIPE,
        stdout=ipc.PIPE,
        stderr=ipc.PIPE
    )
    (stdout, stderr) = child.communicate(stdin)
    if child.returncode != expected_exit_status:
        if str != bytes:
            stderr = stderr.decode('ASCII', 'replace')
        print(stderr)
        raise ipc.CalledProcessError(child.returncode, cmd[0])
    return (stdout, stderr)

def run_afl_showmap(stdin, expected_stdout=None, expected_exit_status=0):
    tmpdir = tempfile.mkdtemp()
    outpath = os.path.join(tmpdir, 'out')
    try:
        (stdout, stderr) = run(
            ['afl-showmap', '-o', outpath, sys.executable, target],
            stdin=stdin,
            expected_exit_status=expected_exit_status,
        )
        if expected_stdout is not None:
            assert_equal(stdout, expected_stdout)
        with open(outpath, 'r') as file:
            return file.read()
    finally:
        shutil.rmtree(tmpdir)

def test_diff():
    out1 = run_afl_showmap(b'0', b'Looks like a zero to me!\n')
    out2 = run_afl_showmap(b'1', b'A non-zero value? How quaint!\n')
    assert_not_equal(out1, out2)

def test_exception():
    out = run_afl_showmap(b'\xff', expected_exit_status=2)
    assert_not_equal(out, b'')

# vim:ts=4 sts=4 sw=4 et