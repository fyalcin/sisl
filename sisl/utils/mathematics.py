from __future__ import print_function, division

from numbers import Integral
from math import pi
from math import factorial as fact
import math as m

import numpy as np
from numpy import dot, asarray
from numpy import cos, sin, arctan2, arccos
from numpy import take, sqrt, square

from sisl import _array as _a
from sisl._help import ensure_array

__all__ = ['fnorm', 'fnorm2', 'expand', 'orthogonalize']
__all__ += ['spher2cart', 'cart2spher', 'spherical_harm']


def fnorm(array):
    r""" Fast calculation of the norm of a vector

    Parameters
    ----------
    array : (..., *)
       the vector/matrix to perform the norm on, norm performed on last axis
    """
    return sqrt(square(array).sum(-1))


def fnorm2(array):
    r""" Fast calculation of the squared norm of a vector

    Parameters
    ----------
    array : (..., *)
       the vector/matrix to perform the squared norm on, norm performed on last axis
    """
    return square(array).sum(-1)


def expand(vector, length):
    r""" Expand `vector` by `length` such that the norm of the vector is increased by `length`

    The expansion of the vector can be written as:

    .. math::
        V' = V + \hat V l

    Parameters
    ----------
    vector : array_like
        original vector
    length : float
        the length to be added along the vector

    Returns
    -------
    new_vector : the new vector with increased length
    """
    return vector * (1 + length / fnorm(vector))


def orthogonalize(ref, vector):
    r""" Ensure `vector` is orthogonal to `ref`, `vector` must *not* be parallel to `ref`.

    Enable an easy creation of a vector orthogonal to a reference vector. The length of the vector
    is not necessarily preserved (if they are not orthogonal).

    The orthogonalization is performed by:

    .. math::
       V_{\perp} = V - \hat R (\hat R \cdot V)

    which is subtracting the projected part from :math:`V`.

    Parameters
    ----------
    ref : array_like
       reference vector to make `vector` orthogonal too
    vector : array_like
       the vector to orthogonalize, must have same dimension as `ref`

    Returns
    -------
    ortho : the orthogonalized vector

    Raises
    ------
    ValueError : if `vector` is parallel to `ref`
    """
    ref = asarray(ref).ravel()
    nr = fnorm(ref)
    vector = asarray(vector).ravel()
    d = dot(ref, vector) / nr
    if abs(1. - abs(d) / fnorm(vector)) < 1e-7:
        raise ValueError("orthogonalize: requires non-parallel vectors to perform an orthogonalization: ref.vector = {}".format(d))
    return vector - ref * d / nr


def spher2cart(r, theta, phi):
    r""" Convert spherical coordinates to cartesian coordinates

    Parameters
    ----------
    r : array_like
       radius
    theta : array_like
       azimuthal angle in the :math:`x-y` plane
    phi : array_like
       polar angle from the :math:`z` axis
    """
    rx = r * cos(theta) * sin(phi)
    R = _a.emptyd(rx.shape + (3, ))
    R[..., 0] = rx
    del rx
    R[..., 1] = r * sin(theta) * sin(phi)
    R[..., 2] = r * cos(phi)
    return R


def cart2spher(r, theta=True, cos_phi=False, maxR=None):
    r""" Transfer a vector to spherical coordinates with some possible differences

    Parameters
    ----------
    r : array_like
       the cartesian vectors
    theta : bool, optional
       if ``True`` also calculate the theta angle and return it
    cos_phi : bool, optional
       if ``True`` return :math:`\cos(\phi)` rather than :math:`\phi` which may
       be useful in some subsequent mathematical calculations
    maxR : float, optional
       cutoff of the spherical coordinate calculations. If ``None``, calculate
       and return for all.

    Returns
    -------
    n : int
       number of total points, only for `maxR` different from ``None``
    idx : numpy.ndarray
       indices of points with ``r <= maxR``
    r : numpy.ndarray
       radius in spherical coordinates, only for `maxR` different from ``None``
    theta : numpy.ndarray
       angle in the :math:`x-y` plane from :math:`x` (azimuthal)
       Only returned if input `theta` is ``True``
    phi : numpy.ndarray
       If `cos_phi` is ``True`` this is :math:`\cos(\phi)`, otherwise
       :math:`\phi` is returned (the polar angle from the :math:`z` axis)
    """
    r = ensure_array(r, np.float64).reshape(-1, 3)
    if r.shape[-1] != 3:
        raise ValueError("Vector does not end with shape 3.")
    n = r.shape[0]
    if maxR is None:
        rr = sqrt(square(r).sum(1))
        theta = arctan2(r[:, 1], r[:, 0])
        if cos_phi:
            phi = r[:, 2] / rr
        else:
            phi = arccos(r[:, 2] / rr)
        phi[rr == 0.] = 0.
        return rr, theta, phi

    rr = square(r).sum(1)
    idx = (rr <= maxR ** 2).nonzero()[0]
    r = take(r, idx, 0)
    rr = sqrt(take(rr, idx))
    if theta:
        theta = arctan2(r[:, 1], r[:, 0])
    else:
        theta = None
    if cos_phi:
        phi = r[:, 2] / rr
    else:
        phi = arccos(r[:, 2] / rr)
    # Typically there will be few rr==0. values, so no need to
    # create indices
    phi[rr == 0.] = 0.
    return n, idx, rr, theta, phi


def spherical_harm(m, l, theta, phi):
    r""" Calculate the spherical harmonics using :math:`Y_l^m(\theta, \varphi)` with :math:`\mathbf R\to \{r, \theta, \varphi\}`.

    .. math::
        Y^m_l(\theta,\varphi) = (-1)^m\sqrt{\frac{2l+1}{4\pi} \frac{(l-m)!}{(l+m)!}}
             e^{i m \theta} P^m_l(\cos(\varphi))

    which is the spherical harmonics with the Condon-Shortley phase.

    Parameters
    ----------
    m : int
       order of the spherical harmonics
    l : int
       degree of the spherical harmonics
    theta : array_like
       angle in :math:`x-y` plane (azimuthal)
    phi : array_like
       angle from :math:`z` axis (polar)
    """
    # Probably same as:
    #return (-1) ** m * ( (2*l+1)/(4*pi) * factorial(l-m) / factorial(l+m) ) ** 0.5 \
    #    * lpmv(m, l, np.cos(theta)) * np.exp(1j * m * phi)
    return sph_harm(m, l, theta, phi) * (-1) ** m