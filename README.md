# Analyzing Solar Irradiance Variation From GPS and Cameras

With the spirit of reproducible research, this repository contains all the codes required to produce the results in the manuscript: 

> S. Manandhar\*, S. Dev\*, Y. H. Lee and Y. S. Meng, Analyzing Solar Irradiance Variation From GPS and Cameras, IEEE AP-S Symposium on Antennas and Propagation and USNC-URSI Radio Science Meeting, 2018 (\* Authors contributed equally).

Please cite the above paper if you intend to use whole/part of the code. This code is only for academic and research purposes.

![alt text](https://github.com/Soumyabrata/irradiance-variation/blob/master/input/relation.png)

*It  is  clear  that  with  increasing  PWV values, both the net cloud radiative effect and cloud coverage increases.*

## Code Organization
All codes are written in python. The scripts are tested with `Python 3.5.4 `.

### Code 
The scripts to reproduce the figures in the paper are as follows:
* `calculateBoxPlot.py`: Computes the box plots to understand the relation between PWV, cloud radiative effect and cloud coverage.
* `cloud_coverage_example.py`: Illustrates cloud coverage computation.

Other user-defined python scripts are kept in the folder `scripts`.

### Data 
We also share the dataset used in the paper. We collect the data from the rooftop of a building at Nanyang Technological University Singapore. All the input files are kept in the folder `input`.



