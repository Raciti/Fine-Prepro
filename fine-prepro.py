import ants
import argparse
import os
import subprocess
from tqdm import tqdm

def brain_extra(output_path, name):
    try:
        print("Esecution of mri_synthstrip in A")
        subprocess.run(['mri_synthstrip', '-i', f"{os.path.join(output_path, name)}", '-o', f"{os.path.join(output_path, name.split('.')[0])}_brain.nii.gz", '-m', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz"],
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")

    try:
        print("Creation brain_skull A")
        subprocess.run(['fslmaths', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz", '-edge', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz"], 
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")

    try:
        print("Normalizzation brain_skull A")
        subprocess.run(['fslmaths', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz", '-bin', '-mul', '100', f"{os.path.join(output_path, name.split('.')[0])}_brain_mask.nii.gz"], 
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")

def robustfov(mri, out_path):
    try:
        subprocess.run(['robustfov', '-i', mri, '-r', out_path],
                    check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during command execution: {e}")

def process(input_path, ref, output_path, brain_extran, single=True):
    name = input_path.split("/")[-1]
    name_nosubfix = name.split('.')[0]
    print(f"The {name} file is processing.")
    
    if single:
        mri = ants.image_read(input_path)
        print("Registration pahse!!!")
        registration_result = ants.registration(fixed=ref, moving=mri, type_of_transform='SyN')

        out = registration_result['warpedmovout']
        out.to_file(os.path.join(output_path, name_nosubfix + "reg.niigz"))

        print("Robustfov phase!!!")
        robustfov(os.path.join(output_path, name_nosubfix + "reg.niigz"), output_path)
        
        if brain_extran:
            brain_extra(output_path, name)
            
    else:
        new_output = os.path.join(output_path, name_nosubfix)

        os.makedirs(new_output)

        print("Registration pahse!!!")
        mri = ants.image_read(input_path)
        registration_result = ants.registration(fixed=ref, moving=mri, type_of_transform='SyN')

        out = registration_result['warpedmovout']
        out.to_file(os.path.join(new_output, name_nosubfix + "reg.niigz"))

        print("Robustfov phase!!!")
        robustfov(os.path.join(new_output, name_nosubfix + "reg.niigz"), os.path.join(new_output, name))

        if brain_extran:
            brain_extra(new_output, name)

        


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=str, required=True, help="The input can be a single path or a folder containing T1 MRIs.")
    parser.add_argument('--outputs', type=str, required=True, help="The output it must be a path for a folder, if folder don't exist one will be created.")
    parser.add_argument('--brain_extraction', type=int, default=1, help="If this parameter is setup to 1 the process will produce the brain extracion (default = 1 yes).")


    args = parser.parse_args()
    input_path = args.inputs
    output_path = args.outputs
    brain_extran = args.brain_extraction

    assert os.path.exists(input_path), 'input file doesn\'t exist'

    os.makedirs(output_path, exist_ok=True)

    ref = ants.image_read("./utils/MNI152_T1_1mm.nii.gz")

    if os.path.isfile(input_path):

        process(input_path, ref, output_path, brain_extran)

    else:
        mri_list = os.listdir(input_path)

        for mri in tqdm(mri_list):
            process(os.path.join(input_path, mri), ref, output_path, brain_extran, single=False)


