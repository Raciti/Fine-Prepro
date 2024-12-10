import ants
import argparse
import os
import subprocess
from tqdm import tqdm
import nibabel as nib
import numpy as np

def brain_extraction(output_path, name, namer=''):

    n = name if namer == '' else namer

    try:
        print("Esecution of mri_synthstrip in A")
        subprocess.run(['mri_synthstrip', '-i', f"{os.path.join(output_path, n)}", '-o', f"{os.path.join(output_path, name.split('.')[0].replace('_rob', ''))}_brain.nii.gz", '-m', f"{os.path.join(output_path, name.split('.')[0].replace('_rob', ''))}_brain_mask.nii.gz"],
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")
        exit()

    try:
        print("Creation brain_skull A")
        subprocess.run(['fslmaths', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz", '-edge', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz"], 
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")
        exit()

    try:
        print("Normalizzation brain_skull A")
        subprocess.run(['fslmaths', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz", '-bin', '-mul', '100', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz"], 
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")
        exit()


def robustfov(mri, out_path):
    print("Robustfov phase!!!")
    try:
        subprocess.run(['robustfov', '-i', mri, '-r', out_path],
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")
        exit()

def percnorm_nifti(mri, lperc, uperc):
    norm_arr = percnorm(mri.get_fdata(), lperc, uperc)
    return nib.Nifti1Image(norm_arr, mri.affine, mri.header)

def percnorm(arr, lperc, uperc):
    upperbound = np.percentile(arr, uperc)
    lowerbound = np.percentile(arr, lperc)
    arr[arr > upperbound] = upperbound
    arr[arr < lowerbound] = lowerbound
    return arr

def normalizzazion(file_path, o_path, lperc, uperc):
    mri = nib.load(file_path)
    norm_mri = percnorm_nifti(mri, lperc, uperc)
    nib.save(norm_mri, o_path)

def process(input_path, output_path, norm, brain_extran, robust, single=True, lperc=1, uperc=99):
    
    ref = ants.image_read("./utils/MNI152_T1_1mm.nii.gz")
    
    name = input_path.split("/")[-1]
    name_nosubfix = name.split('.')[0]
    print(f"The {name} file is processing.")
    
    if single:
        mri = ants.image_read(input_path)
        print("Registration pahse!!!")
        registration_result = ants.registration(fixed=ref, moving=mri, type_of_transform='SyN')

        out = registration_result['warpedmovout']
        name_reg = name_nosubfix + "_reg.nii.gz"
        out.to_file(os.path.join(output_path, name_reg))

        if norm:
            name_norm = name_nosubfix + "_norm.nii.gz"
            normalizzazion(os.path.join(output_path, name_reg), os.path.join(output_path, name_norm), lperc, uperc)

        if robust:
            name_rob = name_nosubfix + '_rob.nii.gz'
            robustfov(os.path.join(output_path, name_norm), os.path.join(output_path, name_rob)) if norm else robustfov(os.path.join(output_path, name_reg), os.path.join(output_path, name_rob))
        
        if brain_extran:
            brain_extraction(output_path, name, name_rob) if robust else brain_extraction(output_path, name) 
            
    else:
        new_output = os.path.join(output_path, name_nosubfix)

        os.makedirs(new_output)

        print("Registration pahse!!!")
        mri = ants.image_read(input_path)
        registration_result = ants.registration(fixed=ref, moving=mri, type_of_transform='SyN')

        out = registration_result['warpedmovout']
        name_reg = name_nosubfix + "_reg.nii.gz"
        out.to_file(os.path.join(new_output, name_reg))

        if norm:
            name_norm = name_nosubfix + "_norm.nii.gz"
            normalizzazion(os.path.join(new_output, name_reg), os.path.join(new_output, name_norm), lperc, uperc)

        if robust:
            name_rob = name_nosubfix + '_rob.nii.gz'
            robustfov(os.path.join(new_output, name_norm), os.path.join(new_output, name_rob)) if norm else robustfov(os.path.join(new_output, name_reg), os.path.join(new_output, name_rob))

        if brain_extran:
            brain_extraction(new_output, name, name_rob) if robust else brain_extraction(new_output, name) 

        


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Fine-Preprocessing")
    parser.add_argument('--inputs', type=str, required=True, help="The input can be a single path or a folder containing T1 MRIs.")
    parser.add_argument('--outputs', type=str, required=True, help="The output it must be a path for a folder, if folder don't exist one will be created.")
    parser.add_argument('--norm', type=int, default=0, help="Remove outlier intensities from a brain component, similar to Tukey's fences method.")
    parser.add_argument('--robustfov', type=int, default=1, help="This flag hallows use of robustfov, whit center the brain, eliminating slices from the z axis (default use robustfov).")
    parser.add_argument('--brain_extraction', type=int, default=1, help="If this parameter is setup to 1 the process will produce the brain extracion (default = 1 yes).")


    args = parser.parse_args()
    input_path = args.inputs
    output_path = args.outputs
    norm = args.norm
    robust = args.robustfov
    brain_extran = args.brain_extraction

    assert os.path.exists(input_path), 'input file doesn\'t exist'
    assert norm in (0,1), 'norm can be 0 or 1' 
    assert robust in (0,1), 'robustfov can be 0 or 1' 
    assert brain_extran in (0,1), 'brain_extraction can be 0 or 1' 

    os.makedirs(output_path, exist_ok=True)

    if os.path.isfile(input_path):

        process(input_path, output_path, norm, brain_extran, robust)

    else:
        mri_list = os.listdir(input_path)

        for mri in tqdm(mri_list):
            process(os.path.join(input_path, mri), output_path, norm, brain_extran,robust, single=False)


