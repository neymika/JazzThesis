# JazzThesis
Jazz Accompaniment Generation Project under Professor Minnich

## Pre-Term
  * Conducted preliminary research about current models and tools available.
    * In Google Drive only accessible to [Caltech](https://docs.google.com/document/d/194IrzHoIaE3tV-BhLnm9dzZ_iBV8fqSgp4qFqe_i6mw/edit?usp=sharing)
## Week 1
  * (NJ) Implemented data scrapper to download all MIDI files from [Doug McKenzie's website](https://bushgrafts.com/midi/)
    * Requires the following package installations:
      * ```python
        pip3 install requests
        pip3 install bs4
        pip3 install html5lib
        ```
    * To run file:
      * ```python
        cd Data
        python3 datascrapper.py
        ```
  * (NJ and NA) Currently trying to adjust MIDI manipulations and classifications from CS 159 VAE code
