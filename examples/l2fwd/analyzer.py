#! /usr/bin/python3

import argparse
from enum import Enum
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('path', help='path to fifo object')
args = parser.parse_args()

TESTS_TO_SKIP = 30
ACCURACY = 0.99
RELIABILITY = 0.95
MAX_LOSS_EXCESS = 1.46
C = 0.41
EPS = (1 - RELIABILITY) / 10
U = 1.96  # U_((1+RELIABILITY)/2) = U_97.5 = 1.96 (via table at Wikipedia)


class Analyzer:
    class Mode(Enum):
        study = 1
        diagnose = 2

    def __init__(self, fifo):
        try:
            self.fifo = open(fifo)
        except FileNotFoundError:
            print("fifo not found. Exiting...")
            exit()
        self.mode = self.Mode.study
        self.normal_hit_rate = None

    def __del__(self):
        self.fifo.close()

    def __call__(self):
        hit_rates = []
        last_print_time = 0
        for line in self.fifo:
            hit_rate = float(line.strip())
            hit_rates.append(hit_rate)
            if len(hit_rates) <= TESTS_TO_SKIP:
                continue

            ev = self.calculate_ev(hit_rates)
            dispersion = self.calculate_dispersion(hit_rates, ev)
            moment = self.calculate_moment(hit_rates, ev)

            if self.mode == self.Mode.study:
                check = self.calculate_estimation1(len(hit_rates), dispersion)
                check = check and self.calculate_estimation2(len(hit_rates), dispersion, moment)
                if check:
                    self.normal_hit_rate = ev
                    self.mode = self.Mode.diagnose
            if self.mode == self.Mode.diagnose:
                if hit_rate < self.normal_hit_rate / MAX_LOSS_EXCESS and time.time() - last_print_time > 1:
                    print("{}: Degradation with hit rate {} over normal {}".format(time.ctime(), hit_rate, self.normal_hit_rate))
                    last_print_time = time.time()

    def calculate_ev(self, hit_rates):
        return sum(hit_rates) / len(hit_rates)

    def calculate_dispersion(self, hit_rates, ev):
        sum = 0
        for hit_rate in hit_rates:
            sum += (hit_rate - ev)**2
        sum /= len(hit_rates) - 1
        return sum

    def calculate_moment(self, hit_rates, ev):
        sum = 0
        for hit_rate in hit_rates:
            sum += (hit_rate - ev)**3
        sum /= len(hit_rates) - 1
        return sum

    def calculate_estimation1(self, count, dispersion):
        return count > (U / ACCURACY)**2 * dispersion

    def calculate_estimation2(self, count, dispersion, moment):
        return C * moment / dispersion**(3/2) / count**(1/2) <= EPS
