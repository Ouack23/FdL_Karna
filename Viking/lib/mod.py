# -*- coding: utf-8 -*-
#
# This file define modulation opperations
#

import numpy as np

def linear_modulation(capteur, coef):
    """
    This function calculate the delta hsv matrice
    :param capteur: (3*9) matrice with (3*3) matrice for each parameter (H,S,V) from the capteur value
    :param coef: (3*9) matrice with (3*3) matrice for each parameter (H,S,V)
    :return: HSV delta modulation matrice
    """
    mat = capteur*coef
    return np.float32((mat[0:3].sum(), mat[3:6].sum(), mat[6:9].sum()))

def compute_capteur_matrice_from_capteur(capteur):
    """
    This function return the matrice of lin, exp and log value of the given capteur
    :param capteur: (3*1) matrice of capteur value
    :return: (3*9) matrice with lin, exp and log values
    """
    mat = np.vstack((capteur, np.exp(capteur), np.log(capteur)))
    return np.vstack((mat, mat, mat))

def compute_all_capteurs_matrice(capteur1,capteur2):
    """
    This function compute a (9 * 15) matrice with C1, C2, C1*C2, C1-C2 and C2-C1
    :param capteur1: (3*1) matrice of capteur value for capteur 1
    :param capteur2: (3*1) matrice of capteur value for capteur 1
    :return: (9*15) all capteur matrice
    """
    mat_c1 = compute_capteur_matrice_from_capteur(capteur1)
    mat_c2 = compute_capteur_matrice_from_capteur(capteur2)
    mat_c1c2 = compute_capteur_matrice_from_capteur(capteur1*capteur2)
    mat_c1_c2 = compute_capteur_matrice_from_capteur(capteur1-capteur2)
    mat_c2_c1 = compute_capteur_matrice_from_capteur(capteur2-capteur1)
    return np.hstack((mat_c1, mat_c2, mat_c1c2, mat_c1_c2, mat_c2_c1))


def compute_modulation(capteur, coef):
    """
    This function compute the total modulation with C1, C2, C1*C2, C1-C2 and C2-C1
    :param capteur: (9*15) all capteur matrice
    :param coef: (9*15) all coef matrice
    :return: 3 values tuple (HSV)
    """
    mat = np.nansum(capteur * coef, axis=1)
    return mat[0:3].sum(), mat[3:6].sum(), mat[6:9].sum()


