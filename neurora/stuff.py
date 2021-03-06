# -*- coding: utf-8 -*-

' a module for some simple but important processes '

__author__ = 'Zitong Lu'

import nibabel as nib
import numpy as np
import os
import math

# get package abspath
package_root = os.path.dirname(os.path.abspath(__file__))


' a function for zeroing the value close to zero '

def limtozero(x):

    """
    zero the value close to zero

    Parameters
    ----------
    x : float

    Returns
    -------
    0
    """

    if x < 1e-15:
        x = 0

    return x


' a function for getting the affine of the fMRI-img '

def get_affine(file_name):

    """
    get the affine of the fMRI-img

    Parameters
    ----------
    file_name : string
        The filename of a sample fMRI-img in your experiment

    Returns
    -------
    affine : array
        The position information of the fMRI-image array data in a reference space.
    """

    img = nib.load(file_name)

    return img.affine


' a function for FWE-correction for fMRI RSA results '

def fwe_correct(p):

    """
    FWE correction for fMRI RSA results

    p : array
        The p-value map (3-D).
    """

    px = np.shape(p)[0]
    py = np.shape(p)[1]
    pz = np.shape(p)[2]

    n = 0

    for i in range(px):
        for j in range(py):
            for k in range(pz):

                if (math.isnan(p[i, j, k]) == False) and (p[i, j, k] != 0):
                    n = n + 1

    fwep = p*n

    print("finished FWE correct")

    return fwep


' a function for FDR-correction for fMRI RSA results '

def fdr_correct(p):

    """
    FDR correction for fMRI RSA results

    Parameters
    ----------
    p : array
        The p-value map (3-D).

    Returns
    -------
    correctp : array.
        The FDR corrected p-value map.
    """

    px = np.shape(p)[0]
    py = np.shape(p)[1]
    pz = np.shape(p)[2]

    n = 0

    for i in range(px):
        for j in range(py):
            for k in range(pz):

                if (math.isnan(p[i, j, k]) == False) and (p[i, j, k] != 0):

                    n = n + 1

    fdrp = np.full([px, py, pz], np.nan)

    pcluster = np.zeros([n], dtype=np.float)

    m = 0

    for i in range(px):
        for j in range(py):
            for k in range(pz):

                if (math.isnan(p[i, j, k]) == False) and p[i, j, k] != 0:
                    pcluster[m] = p[i, j, k]
                    m = m + 1

    index = np.argsort(pcluster)

    for l in range(n):
        pcluster[index[l]] = float(pcluster[index[l]] * n / (l + 0.5))

    """for l in range(n - 1):
        if pcluster[index[-l - 1]] < pcluster[index[-l - 2]]:
            pcluster[index[-l - 2]] = pcluster[index[-l - 1]]"""

    newpcluster = np.full([n], np.nan)

    for l in range(n):
        newpcluster[l] = pcluster[index[l]]

    m = 0

    for i in range(px):
        for j in range(py):
            for k in range(pz):

                if (math.isnan(p[i, j, k]) == False) and p[i, j, k] != 0:
                    fdrp[i, j, k] = newpcluster[m]
                    m = m + 1

    print("finished FDR correct")

    return fdrp

"""def fdr_correct(p, size=[60, 60, 60], n=64, type="sphere"):

    x = size[0]
    y = size[1]
    z = size[2]

    px = np.shape(p)[0]
    py = np.shape(p)[1]
    pz = np.shape(p)[2]

    if type == "cube":

        n = float(n*px*py*pz/(x*y*z))

        nq = 1
        ni = 1

        while nq < n:
            ni = ni + 1
            nq = ni*ni*ni

        n = nq

        print(n, ni)

        fdrp = np.full([px, py, pz], np.nan)

        for i in range(px-ni+1):
            for j in range(py-ni+1):
                for k in range(pz-ni+1):

                    pcluster = p[i:i+ni, j:j+ni, k:k+ni]
                    pcluster = np.reshape(pcluster, [n])

                    index = np.argsort(pcluster)

                    for l in range(n):
                        pcluster[index[l]] = float(pcluster[index[l]]*n/(l+1))

                    for l in range(n-1):
                        if pcluster[index[-l-1]] < pcluster[index[-l-2]]:
                            pcluster[index[-l-2]] = pcluster[index[-l-1]]

                    newpcluster = np.full([n], np.nan)

                    for l in range(n):
                        newpcluster[l] = pcluster[index[l]]

                    fdrp[i:i+ni, j:j+ni, k:k+ni] = np.reshape(newpcluster, [ni, ni, ni])

        print("finished FDR correct")

        return fdrp

    elif type == "sphere":

        ni = int(nr * px * py * pz / (x * y * z)) + 1

        c0 = [int(ni), int(ni), int(ni)]
        n0 = 0
        for i in range(int(2 * ni + 1)):
            for j in range(int(2 * ni + 1)):
                for k in range(int(2 * ni + 1)):
                    dist = np.square(i - c0[0]) + np.square(j - c0[1]) + np.square(k - c0[2])
                    if dist <= ni * ni:
                        # print(i, j)
                        n0 = n0 + 1

        n = n0
        # print(c0)
        # print(n0)
        print(n, ni)

        fdrp = np.full([px, py, pz], np.nan)

        for i in range(px - 2 * ni):
            for j in range(py - 2 * ni):
                for k in range(pz - 2 * ni):

                    nindex = 0

                    pcluster = np.zeros([n], dtype=np.float)

                    for lx in range(2 * ni + 1):
                        for ly in range(2 * ni + 1):
                            for lz in range(2 * ni + 1):
                                dist = np.square(lx - c0[0]) + np.square(ly - c0[1]) + np.square(lz - c0[2])
                                if dist <= ni * ni:
                                    pcluster[nindex] = p[i + lx, j + ly, k + lz]
                                    nindex = nindex + 1

                    index = np.argsort(pcluster)

                    for l in range(n):
                        pcluster[index[l]] = float(pcluster[index[l]] * n / (l + 1))

                    for l in range(n - 1):
                        if pcluster[index[-l - 1]] < pcluster[index[-l - 2]]:
                            pcluster[index[-l - 2]] = pcluster[index[-l - 1]]

                    newpcluster = np.full([n], np.nan)

                    for l in range(n):
                        newpcluster[l] = pcluster[index[l]]

                    nindex = 0

                    for lx in range(2 * ni + 1):
                        for ly in range(2 * ni + 1):
                            for lz in range(2 * ni + 1):
                                dist = np.square(lx - c0[0]) + np.square(ly - c0[1]) + np.square(lz - c0[2])
                                if dist <= ni * ni:
                                    fdrp[i + lx, j + ly, k + lz] = newpcluster[nindex]
                                    nindex = nindex + 1

        print("finished FDR correct")

        return fdrp"""


' a function for fMRI RSA results correction by threshold '

def correct_by_threshold(img, threshold):

    """
    correct the fMRI RSA results by threshold

    Parameters
    ----------
    img : array
        A 3-D array of the fMRI RSA results.
        The shape of img should be [nx, ny, nz]. nx, ny, nz represent the shape of the fMRI-img.
    threshold : int
        The number of voxels used in correction.
        If threshold=n, only the similarity clusters consisting more than n voxels will be visualized.

    Returns
    -------
    img : array
        A 3-D array of the fMRI RSA results after correction.
        The shape of img should be [nx, ny, nz]. nx, ny, nz represent the shape of the fMRI-img.
    """

    sx = np.shape(img)[0]
    sy = np.shape(img)[1]
    sz = np.shape(img)[2]

    nsmall = 1

    while nsmall*nsmall*nsmall < threshold:
        nsmall = nsmall + 1

    nlarge = nsmall + 2

    for i in range(sx-nlarge+1):
        for j in range(sy-nlarge+1):
            for k in range(sz-nlarge+1):

                listlarge = list(np.reshape(img[i:i+nlarge, j:j+nlarge, k:k+nlarge], [nlarge*nlarge*nlarge]))
                print(listlarge.count(0))

                if listlarge.count(0) < nlarge*nlarge*nlarge:

                    index1 = 0

                    for l in range(nlarge):
                        for m in range(nlarge):

                            if img[i + l, j + m, k] == 0:
                                index1 = index1 + 1

                            if img[i + l, j + m, k + nlarge - 1] == 0:
                                index1 = index1 + 1

                    for l in range(nlarge-1):
                        for m in range(nlarge-2):

                            if img[i + l, j, k + m] == 0:
                                index1 = index1 + 1

                            if img[i, j + l + 1, k + m] == 0:
                                index1 = index1 + 1

                            if img[i + nlarge - 1, j + l, k + m] == 0:
                                index1 = index1 + 1

                            if img[i + l + 1, j + nlarge - 1, k + m] == 0:
                                index1 = index1 + 1

                    nex = nlarge * nlarge * nlarge - nsmall * nsmall * nsmall
                    print("index1:"+str(index1))

                    if index1 == nex:
                        print("**************************")
                        unit = img[i+1:i+1+nsmall, j+1:j+1+nsmall, k+1:k+1+nsmall]
                        unit = np.reshape(unit, [nsmall*nsmall*nsmall])
                        list_internal = list(unit)
                        index2 = nsmall*nsmall*nsmall-list_internal.count(0)
                        print(index1, index2)

                        if index2 < threshold:
                            img[i+1:i+1+nsmall, j]

                            for l in range(nsmall):
                                for m in range(nsmall):
                                    for p in range(nsmall):
                                        img[i+1:i+1+nsmall, j+1:j+1+nsmall, k+1:k+1+nsmall] = np.zeros([nsmall, nsmall, nsmall])

    print("finished correction")

    return img


' a function for getting ch2.nii.gz '

def get_bg_ch2():

    """
    get ch2.nii.gz

    Returns
    -------
    path : string
        The absolute file path of 'ch2.nii.gz'
    """

    return os.path.join(package_root, 'template/ch2.nii.gz')


' a function for getting ch2bet.nii.gz '

def get_bg_ch2bet():

    """
    get ch2bet.nii.gz

    Returns
    -------
    path : string
        The absolute file path of 'ch2bet.nii.gz'
    """

    return os.path.join(package_root, 'template/ch2bet.nii.gz')


' a function for filtering the data by a ROI mask '

def datamask(fmri_data, mask_data):

    """
    filter the data by a ROI mask

    Parameters:
    fmri_data : array
        The fMRI data.
        The shape of fmri_data is [nx, ny, nz]. nx, ny, nz represent the size of the fMRI data.
    mask_data : array
        The mask data.
        The shape of mask_data is [nx, ny, nz]. nx, ny, nz represent the size of the fMRI data.

    Returns
    -------
    newfmri_data : array
        The new fMRI data.
        The shape of newfmri_data is [nx, ny, nz]. nx, ny, nz represent the size of the fMRI data.
    """

    nx, ny, nz = fmri_data.shape

    newfmri_data = np.full([nx, ny, nz], np.nan)

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):

                if (mask_data[i, j, k] != 0) and (math.isnan(mask_data[i, j, k]) is False):
                    newfmri_data[i, j, k] = fmri_data[i, j, k]

    return newfmri_data