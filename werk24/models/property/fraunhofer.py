from enum import Enum


class W24FraunhoferLine(str, Enum):
    """
    In optics, the "d" and "e" lines refer to specific spectral lines
    associated with the emission spectrum of hydrogen. They are used
    as standard reference points for calibrating optical instruments
    and for characterizing optical materials like glass and lenses.

    The "d-line" typically refers to the Fraunhofer line, which
    is the major spectral line in the yellow region of the
    spectrum emitted by sodium (Na). It is actually a doublet,
    with wavelengths approximately at 589.0 nm (D2) and 589.6 nm (D1).
    The d-line is often used in the testing of optical components
    due to its narrow bandwidth and its position in the spectrum
    close to the maximum sensitivity of the human eye.

    The "e-line" is also a spectral line associated with mercury (Hg)
    emission. It has a wavelength of about 546.1 nm and falls within
    the green part of the spectrum. The e-line is also used in the
    characterization of optical systems.
    """

    D_LINE = "D_LINE"
    E_LINE = "E_LINE"
