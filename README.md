# ⚙️ Fine-Prepro 
Preprocessing of MRI for better use in medical tools or AI activities. <br>
In the image below only the axial axis result is shown, but the pipeline works on 3D images
![Results pipeline](https://github.com/Raciti/Fine-Preprocessing/blob/main/utils/Fine-prepro.png)

## Requirements
The following software must be installed to use Fine-Prepro:
* [FSL](https://fsl.fmrib.ox.ac.uk/fs)
* [ANTs](https://github.com/ANTsX/ANTs)


The file requirements.txt contains the libraries used for operation.

# Usage
The files must be **.nii.gz**.

```
usage: fine-prepro.py [-h] --inputs INPUTS --outputs OUTPUTS [--threads THREADS] [--norm NORM]
                      [--robustfov ROBUSTFOV] [--brain_extraction BRAIN_EXTRACTION]
                      [--lperc LPERC] [--uperc UPERC]

*****{Fine-Prepro}*****

options:
  -h, --help            show this help message and exit
  --inputs INPUTS       The input can be a single path or a folder containing T1 MRIs.
  --outputs OUTPUTS     The output it must be a path for a folder, if folder don't exist one will be created.
  --threads THREADS     Threads (default: number of cores).
  --norm NORM           Remove outlier intensities from a brain component, similar to Tukey's fences method.
  --robustfov ROBUSTFOV
                        This flag hallows use of robustfov, whit center the brain, eliminating slices from the z axis (default use robustfov).
  --brain_extraction BRAIN_EXTRACTION
                        If this parameter is setup to 1 the process will produce the brain extracion (default = 1 yes).

Normalizzation optzions:
  --lperc LPERC         Indicate the lower percentile number you want to consider (default 0).
  --uperc UPERC         Indicate the upper percentile number you want to consider (default 99).
```


The input (`--inputs`) can be:
* a path to nii.gz imaga
  
```
./path/to/.nii.gz
```
* a path to folder that contains MRIs
```
./path/to/folder
```
The outuput (`--outputs`) must be a path to a folder, if it does't exist it will be created.
```
./path/to/output_folder
``` 

# Pipeline
| Phase | Algortihm | Library |
|-----------------|----------------|----------------|
| Registration   | registration   | `ANTsPy`   |
| Normalization   |   |  `python` |
| ROI   | robustfov  | `FSL`   |
| Skull-stripping  | mri_synthstrip  |  `ANTs`  |
| Brain-mask   |   |  `python`  |

Where it says `python` means that code was used to perform the task
