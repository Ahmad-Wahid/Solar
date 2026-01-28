
import numpy as np

def day_of_year(date):
    return date.timetuple().tm_yday

def declination(n):
    return np.deg2rad(23.45 * np.sin(np.deg2rad(360/365 * (284 + n))))

def hour_angle(local_time):
    return np.deg2rad(15 * (local_time - 12))

def sun_elevation(phi, delta, omega):
    return np.arcsin(
        np.sin(phi)*np.sin(delta) +
        np.cos(phi)*np.cos(delta)*np.cos(omega)
    )

def sun_azimuth(phi, delta, omega, h):
    sin_as = np.cos(delta)*np.sin(omega)/np.cos(h)
    cos_as = (np.sin(h)*np.sin(phi)-np.sin(delta))/(np.cos(h)*np.cos(phi))
    return np.arctan2(sin_as, cos_as)
