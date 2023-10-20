#!/usr/bin/env python
import numpy as np


def write_camino(waveforms, dt, filename):
    """
    Prepares and writes a Camino-compatible scheme file from a collection of 
    waveforms.

    Parameters
    ----------
    waveforms : sequence of arrays, each of shape (nb_timesteps, 3)
        An array of gradient trajectories (unit: T/m).
    dt : float
        Timestep (unit: s)
    filename : string
    """
    with open(filename, "w") as schemefile:
        schemefile.write("VERSION: GRADIENT_WAVEFORM\n")
        for waveform in waveforms:
            nb_timesteps, _ = waveform.shape
            schemefile.write("%d %.3f " % (nb_timesteps, dt))
            for k in range(nb_timesteps):
                schemefile.write("%.6f %.6f %.6f " % \
                  (waveform[k, 0], waveform[k, 1], waveform[k, 2]))
            schemefile.write("\n")
    schemefile.close()


def read_camino(filename):
    """
    Reads a Camino-compatible scheme file and returns the corresponding 
    waveforms.

    Parameters
    ----------
    filename : string

    Returns
    -------
    waveforms : sequence of arrays, each of shape (nb_timesteps, 3)
        A sequence of arrays of gradient trajectories (unit: T/m).
    dt : float
        Timestep (unit: s)
    """
    with open(filename, "r") as schemefile:
        header = schemefile.readline()
        if header.find("GRADIENT_WAVEFORM") == -1:
            raise ValueError("Expecting a Camino-like waveform description.")
        waveforms = []
        dt = 0
        line = schemefile.readline() 
        while line:
            values = np.fromstring(line, sep=" ")
            nb_timesteps = int(values[0])
            dt = values[1]
            waveform = values[2:]
            print(nb_timesteps, dt, waveform.shape)
            if waveform.shape[0] != nb_timesteps * 3:
                raise ValueError("Expected number of timesteps mismatch.")
            waveform = waveform.reshape((nb_timesteps, 3))
            waveforms.append(waveform)
            line = schemefile.readline() 
        return waveforms, dt


if __name__ == "__main__":
    # A simple "test" : create a waveform, write to disk, read from disk and
    # compare to original
    te = 100e-3 
    nb_timesteps = 101
    gmax = 80e-3
    ts = np.linspace(0, te, nb_timesteps)
    dt = ts[1] - ts[0]
    waveform = gmax * np.array([np.sin(2 * np.pi * ts / te),
                                np.sin(6 * np.pi * ts / te),
                                np.sin(10 * np.pi * ts / te)]).T
    filename = "test.scheme"
    waveforms = [waveform, waveform]
    write_camino(waveforms, dt, filename)

    waveforms2, dt2 = read_camino(filename)
    if not np.allclose(dt, dt2) or \
       not np.allclose(waveform, waveforms2[0], atol=1e-4):
        raise ValueError("Written file and original waveform mismatch.")
