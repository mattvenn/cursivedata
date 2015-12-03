#!/usr/bin/env python
import sys
import logging
from moves import Moves
from conf import conf
import argparse

if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    moves = Moves()

    parser = argparse.ArgumentParser(description="turn gcodes into servo commands")
    parser.add_argument('--file', required=True, action='store', dest='file', help="file to open")
    args = parser.parse_args()

    can = 0
    with open(args.file) as fh:
        for line in fh.readlines():
            if line.startswith('d'):
                if '0' in line:
                    can = 0
                else:
                    can = 1
            elif line.startswith('g'):
                line = line.lstrip('g')
                x, y = line.split(',')
                moves.add_point(float(x), float(y), can)

    moves.break_segments()
    moves.calc_max_velocity()
    moves.plan_velocity()
    moves.calc_point_times()
    moves.interpolate_pos_by_time()
    moves.calc_string_lengths()
    moves.dump()

