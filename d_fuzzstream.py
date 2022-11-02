from fmic import FMiC
from math import sqrt
import numpy as np

class DFuzzStreamSummarizer:

    def __init__(self, idxSimilarity, min_fmics=5, max_fmics=100, merge_threshold=0.97, radius_factor=1.0, m=2.0):
        self.min_fmics = min_fmics
        self.max_fmics = max_fmics
        self.merge_threshold = merge_threshold
        self.radius_factor = radius_factor
        self.m = m
        self.__fmics = []
        self.VARmemberships = []
        self.idxSimilarity = idxSimilarity
        self.similMatrix = np.zeros((max_fmics, max_fmics, 2))


    def summarize(self, values, timestamp):
        if len(self.__fmics) < self.min_fmics:
            self.__fmics.append(FMiC(values, timestamp))
            return
        
        distance_from_fmics = [self.__euclidean_distance(fmic.center, values) for fmic in self.__fmics]
        self.VARmemberships = self.__memberships(distance_from_fmics)
        is_outlier = True

        for idx, fmic in enumerate(self.__fmics):
            if fmic.radius == 0.0:
                # Minimum distance from another FMiC
                radius = min([
                    self.__euclidean_distance(fmic.center, another_fmic.center)
                    for another_idx, another_fmic in enumerate(self.__fmics)
                    if another_idx != idx
                ])
            else:
                radius = fmic.radius * self.radius_factor
            
            if distance_from_fmics[idx] <= radius:
                is_outlier = False
                fmic.timestamp = timestamp

        #self.VARmemberships = self.__memberships(distance_from_fmics)
        if is_outlier:
            if len(self.__fmics) >= self.max_fmics:
                oldest = min(self.__fmics, key=lambda f: f.timestamp)
                self.__fmics.remove(oldest)
                self.VARmemberships.pop(oldest)
            self.__fmics.append(FMiC(values, timestamp))
            self.VARmemberships.append(1)
            #return
        else:
            #print("memberships = ", self.VARmemberships)
            for idx, fmic in enumerate(self.__fmics):
                fmic.assign(values, self.VARmemberships[idx], distance_from_fmics[idx])
            self.__fmics = self.__merge(self.VARmemberships)

        #distance_from_fmics = [self.__euclidean_distance(fmic.center, values) for fmic in self.__fmics]
        #self.VARmemberships = self.__memberships(distance_from_fmics)
        

    def summary(self) :
        return self.__fmics.copy()

    def __merge(self, memberships):
        fmics_to_merge = []
        similarity = 0
        #print("memberships = ", memberships)
        #print("memberships size out =", len(memberships))
        #print("------------------------------------------------")
        #If measure is FMic related
        #if(self.idxSimilarity == 1):
        for i in range(0, len(self.__fmics) - 1):           
            for j in range(i + 1, len(self.__fmics)):
                if(self.idxSimilarity == 1):
                    dissimilarity = self.__euclidean_distance(self.__fmics[i].center, self.__fmics[j].center)
                    sum_of_radius = self.__fmics[i].radius + self.__fmics[j].radius
                    if dissimilarity != 0:
                        similarity = sum_of_radius / dissimilarity
                    else:
                        # Highest value possible
                        similarity = 1.7976931348623157e+308

                    if similarity >= self.merge_threshold:
                        fmics_to_merge.append([i, j, similarity])

        #else:
        #    for i in range(0, len(memberships) - 1):
        #        for j in range(i + 1, len(memberships)):
                    #S2 sim. measure
                elif(self.idxSimilarity == 2):
                    self.similMatrix[i, j, 0] += np.minimum(memberships[i], memberships[j])
                    self.similMatrix[i, j, 1] += np.maximum(memberships[i], memberships[j])
                    similarity = self.similMatrix[i, j, 0] / self.similMatrix[i, j, 1]
                
                #S(A,B) = AM(REF(x_1,y_1), ... REF(x_n, y_n))
                elif(self.idxSimilarity == 3):
                    t = 10
                    self.similMatrix[i, j, 0] += np.power(1 - np.absolute(memberships[i] - memberships[j]), 1/t)
                    self.similMatrix[i, j, 1] += 1
                    similarity = self.similMatrix[i, j, 0] / self.similMatrix[i, j, 1]
                    #print(similarity)

                #S(A,B) = G(O(x_1,y_1), ... O(x_n, y_n))
                # O = product   #G = probabilistic sum -> x1 + x2 − x1 · x2
                elif(self.idxSimilarity == 4):
                    overlap = memberships[i] * memberships[j]                      
                    self.similMatrix[i, j, 0] += self.similMatrix[i, j, 0] + overlap - self.similMatrix[i, j, 0] * overlap 
                    similarity = self.similMatrix[i, j, 0]
                    #print(similarity)

                #S(A,B) = G(O(x_1,y_1), ... O(x_n, y_n))
                #O = min #G = max
                elif(self.idxSimilarity == 5):                     
                    min = np.minimum(memberships[i], memberships[j])
                    self.similMatrix[i, j, 0] += np.maximum(self.similMatrix[i, j, 0], min)
                    similarity = self.similMatrix[i, j, 0]

                    
                #S(A,B) = G(O(x_1,y_1), ... O(x_n, y_n))
                #O = GM        #G = 
                elif(self.idxSimilarity == 6):
                    GM = np.sqrt(memberships[i] * memberships[j])
                    #self.similMatrix[i, j, 0] += 1 - ()
                    #self.similMatrix[i, j, 1] += 1
                #S(A,B) = G(O(x_1,y_1), ... O(x_n, y_n))
                #O = OB        #G = 
                elif(self.idxSimilarity == 7):
                    OB = np.sqrt((memberships[i] * memberships[j]) * np.minimum( memberships[i], memberships[j]))
                    #self.similMatrix[i, j, 0] +=

                #S(A,B) = G(O(x_1,y_1), ... O(x_n, y_n))
                #O = Div       #G = 
                elif(self.idxSimilarity == 8):
                    ODiv = np.sqrt(memberships[i] * memberships[j])                        


                if similarity >= self.merge_threshold:
                    fmics_to_merge.append([i, j, similarity])
                        
        # Sort by most similar
        fmics_to_merge.sort(reverse=True, key=lambda k: k[2])
        merged_fmics_idx = []
        merged_fmics = []

        for (i, j, _) in fmics_to_merge:
            if i not in merged_fmics_idx and j not in merged_fmics_idx:
                merged_fmics.append(FMiC.merge(self.__fmics[i], self.__fmics[j]))
                merged_fmics_idx.append(i)
                merged_fmics_idx.append(j)

        merged_fmics_idx.sort(reverse=True)
        for idx in merged_fmics_idx:
            self.__fmics.pop(idx)
        
        return self.__fmics + merged_fmics

    def __euclidean_distance(self, value_a, value_b):
        sum_of_distances = 0
        for idx, value in enumerate(value_a):
            sum_of_distances += pow(value - value_b[idx], 2)
        return sqrt(sum_of_distances)

    def __memberships(self, distances):
        memberships = []
        for distance_j in distances:
            # To avoid division by 0
            sum_of_distances = 2.2250738585072014e-308
            for distance_k in distances:
                if distance_k != 0:
                    sum_of_distances += pow((distance_j / distance_k), 2. / (self.m - 1.))
            memberships.append(1.0 / sum_of_distances)
        return memberships
