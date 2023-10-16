# RING ligand corrector

The RingLigCorrector is a basic CLI tool to format and correct non-standard ligands in order to
be able to use the [RING-PyMOL](https://github.com/BioComputingUP/ring-pymol) plugin to detect
protein and ligand interactions.

## Install

If you have installed the [RING-PyMOL](https://github.com/BioComputingUP/ring-pymol) plugin already, then the
installation is easy.

Simply download the repo with the RingLigCorrector and use it. The only dependency needed is [Typer](https://typer.tiangolo.com/)
which can be easily installed with pip:
```$ pip install "typer[all]"```

If you haven't installed the RING-PyMOL, the other needed dependency is to have PyMOL installed and available to
your Python environment with which you'll run the tool. 

