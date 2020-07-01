import numpy as np
import nibabel as nib
import os
import matplotlib.pyplot as plt
from comparaison.label import label_suit, label_suiter, label_cnn, label_suiter_cnn


def get_dice(img1, img2):
    """
    :param img1: numpy array reprensting a binary mask with same dimension of img2
    :param img2: nulpy array reprensenting binary mask with same dimension of img1
    :return: Dice coefficient between img1 and 2
    """

    dice = (2 * np.sum(np.logical_and(img1, img2))) / (np.sum(img1) + np.sum(img2))
    return dice


def minimize_label(list_img):
    for img in list_img:
        for label in label_suiter_cnn:
            lab_suiter = label_suiter_cnn.get(label)[0]
            path_suiter = [os.path.join(out_path, 'suiter', dataset, sub_id, 'derivative', 'mask', img, x+'.nii') for x in lab_suiter]
            mask_suiter = [nib.load(x) for x in path_suiter]
            data_suiter = [x.get_fdata() for x in mask_suiter]
            new_mask_suiter = sum(data_suiter)
            new_mask_suiter = nib.Nifti1Image(new_mask_suiter, mask_suiter[0].affine, mask_suiter[0].header)
            os.makedirs(os.path.join('/home/dieudonnem/hpc/out/comparaison/suiter_cnn/mask/suiter', img), exist_ok=True)
            nib.save(new_mask_suiter, os.path.join('/home/dieudonnem/hpc/out/comparaison/suiter_cnn/mask/suiter', img,  label + '.nii'))

            lab_cnn = label_suiter_cnn.get(label)[1]
            path_cnn = [os.path.join(out_path, 'cnn', dataset, sub_id, 'derivative', 'mask', img, x + '.nii') for x in lab_cnn]
            mask_cnn = [nib.load(x) for x in path_cnn]
            data_cnn = [x.get_fdata() for x in mask_cnn]
            new_mask_cnn = sum(data_cnn)
            new_mask_cnn = nib.Nifti1Image(new_mask_cnn, mask_cnn[0].affine, mask_cnn[0].header)
            os.makedirs(os.path.join('/home/dieudonnem/hpc/out/comparaison/suiter_cnn/mask/cnn', img), exist_ok=True)
            nib.save(new_mask_cnn, os.path.join('/home/dieudonnem/hpc/out/comparaison/suiter_cnn/mask/cnn',img, label + '.nii'))


def save_dice_matrix(list_img, soft1, soft2, soft1_mask_path, soft2_mask_path, dict_label) :
    list_label = list(dict_label.keys())
    nb_label = len(list_label)
    for img in list_img:
        print('>>', img)
        dice_matrix = np.zeros((nb_label, nb_label))
        # loop to fill dice_matrix
        for label_1 in list_label:
            for label_2 in list_label:
                print(img, ':', label_1, label_2, '\n')
                # data_1 : soft1 mask
                mask_1 = label_1 + '.nii'
                mri_1 = nib.load(os.path.join(soft1_mask_path, img, mask_1))
                data_1 = mri_1.get_fdata()
                # data_2 : soft2 mask
                mask_2 = label_2 + '.nii'
                mri_2 = nib.load(os.path.join(soft2_mask_path, img, mask_2))
                data_2 = mri_2.get_fdata()
                # fill dice_matrix
                dice_matrix[list_label.index(label_1)][list_label.index(label_2)] = get_dice(data_1, data_2)
        save_dir = os.path.join(out_path, 'comparaison', soft1 + '_' + soft2, dataset, sub_id, 'dice_matrix', img)
        os.makedirs(save_dir, exist_ok=True)
        np.save(os.path.join(save_dir, 'dice_matrix'), dice_matrix)
        print('\t dice_matric for %s save \n' %img )


list_label_name = list(label_suiter_cnn.keys())
list_label_name_suiter = ["suit " + x for x in list_label_name]
list_label_name_cnn = ["cnn " + x for x in list_label_name]
def display(list_img, soft1, soft2, list_label_name_soft1,list_label_name_soft2):
    for img in list_img:
        fig, ax = plt.subplots()
        dice_matrix = np.load(os.path.join(out_path, 'comparaison', soft1 + '_' + soft2, dataset, sub_id, 'dice_matrix', img, 'dice_matrix.npy'))
        im = ax.imshow(dice_matrix)
        ax.set_xticks(np.arange(len(list_label_name_soft1)))
        ax.set_yticks(np.arange(len(list_label_name_soft2)))
        ax.set_xticklabels(list_label_name_soft1)
        ax.set_yticklabels(list_label_name_soft2)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize = "x-small")
        plt.setp(ax.get_yticklabels(), fontsize="x-small")
        for i in range(len(list_label_name)):
            for j in range(len(list_label_name)):
                text = ax.text(j, i, round(dice_matrix[i, j], 2), ha="center", va="center", color="w", fontsize = "xx-small")
        ax.set_title(img)
        fig.tight_layout()
        plt.show()

# for img in list_img:
#     print('>>', img)
#     dice_matrix = np.zeros((nb_label, nb_label))
#     # loop to fill dice_matrix
#     for label_1 in list_label:
#         for label_2 in list_label:
#             print('\t', label_1, label_2, '\n')
#             # data_1 : suit mask
#             mask_1 = label_suit.get(label_1) + '.nii'
#             mri_1 = nib.load(os.path.join(suit_mask_path, img, mask_1))
#             data_1 = mri_1.get_fdata()
#             # data_2 : suiter mask
#             mask_2 = label_suit.get(label_2) + '.nii'
#             mri_2 = nib.load(os.path.join(suiter_mask_path, img, mask_2))
#             data_2 = mri_2.get_fdata()
#             # fill dice_matrix
#             dice_matrix[label_1][label_2] = get_dice(data_1, data_2)
#     save_dir = os.path.join(out_path, 'comparaison', 'suit_suiter', dataset, sub_id, img)
#     if not os.path.exists(save_dir):
#         os.mkdir(save_dir)
#     np.save(os.path.join(save_dir,'dice_matrix'), dice_matrix)
#     print('\t dice_matric for %s save \n' %img )

# display

# list_label_name = list(label_suit.values())
# list_label_name_suit = ["suiter " + x for x in list_label_name]
# list_label_name_suiter = ["suit " + x for x in list_label_name]
#
# for img in list_img:
#     fig, ax = plt.subplots()
#     dice_matrix = np.load(os.path.join(out_path, 'comparaison', 'suit_suiter', dataset, sub_id, img, 'dice_matrix.npy'))
#     im = ax.imshow(dice_matrix)
#     ax.set_xticks(np.arange(len(list_label_name_suit)))
#     ax.set_yticks(np.arange(len(list_label_name_suiter)))
#     ax.set_xticklabels(list_label_name_suit)
#     ax.set_yticklabels(list_label_name_suiter)
#     plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize = "x-small")
#     plt.setp(ax.get_yticklabels(), fontsize="x-small")
#     for i in range(len(list_label_name)):
#         for j in range(len(list_label_name)):
#             text = ax.text(j, i, round(dice_matrix[i, j],2), ha="center", va="center", color="w", fontsize = "xx-small")
#     ax.set_title(img)
#     fig.tight_layout()
#     plt.show()

# main

dataset = 'dataset_sence'
sub_id = 'sub-1'

out_path = '/home/dieudonnem/hpc/out'

suiter_path = os.path.join(out_path, 'suiter')
suiter_mask_path = os.path.join(suiter_path, dataset, sub_id, 'derivative', 'mask')

suit_path = os.path.join(out_path, 'suit')
suit_mask_path = os.path.join(suit_path, dataset, sub_id, 'derivative', 'mask')

list_img = os.listdir(suiter_mask_path)
list_img.sort()
print(list_img)

list_label = list(label_suit.keys())  # list_label is the same for suit and suiter


suiter_path = '/home/dieudonnem/hpc/out/comparaison/suiter_cnn/dataset_sence/sub-1/mask/suiter/'
cnn_path = '/home/dieudonnem/hpc/out/comparaison/suiter_cnn/dataset_sence/sub-1/mask/cnn/'
#save_dice_matrix(list_img, 'suiter', 'cnn', suiter_path, cnn_path, label_suiter_cnn)
# minimize_label(list_img)
display(list_img,'suiter', 'cnn', list_label_name_suiter, list_label_name_cnn)