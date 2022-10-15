from math import sqrt


class FMiC:

    def __init__(self, cf, timestamp):
        self.cf = cf.copy()
        self.m = 1.0
        self.n = 1
        self.ssd = 0.0
        self.timestamp = timestamp
        self.center = cf.copy()
        self.radius = 0.0

    def assign(self, values, membership, distance):
        self.m += membership
        self.n += 1
        self.ssd += membership * pow(distance, 2)

        for idx, value in enumerate(values):
            self.cf[idx] += value * membership

        self.__update_center()
        self.__update_radius()

    def merge(fmic_a, fmic_b):
        merged_fmic = FMiC([], max(fmic_a.timestamp, fmic_b.timestamp))
        for idx, cf_a in enumerate(fmic_a.cf):
            merged_fmic.cf.append(cf_a + fmic_b.cf[idx])
        merged_fmic.m = fmic_a.m + fmic_b.m
        merged_fmic.ssd = fmic_a.ssd + fmic_b.ssd
        merged_fmic.n = fmic_a.n + fmic_b.n
        merged_fmic.center = fmic_a.center.copy()

        merged_fmic.__update_center()
        merged_fmic.__update_radius()

        return merged_fmic

    def __update_center(self):
        for idx, cf_i in enumerate(self.cf):
            self.center[idx] = cf_i / self.m

    def __update_radius(self):
        self.radius = sqrt(self.ssd / self.n)
