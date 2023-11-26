import torch
import torch.nn.functional as F
import numpy as np
import os, argparse
from scipy import misc
from lib.pvt import PolypPVT, PolypPVTtiny
from utils.dataloader import test_dataset
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testsize', type=int, default=352, help='testing size')
    parser.add_argument('--pth_path', type=str, default='/home/nhdang/Polyp-PVT-main/teacher_weights/PolypPVT.pth')
    opt = parser.parse_args()
    # model = PolypPVTtiny()
    model = PolypPVT()
    model.load_state_dict(torch.load(opt.pth_path))
    model.cuda()
    model.eval()
    for _data_name in ['CVC-300', 'CVC-ClinicDB', 'Kvasir', 'CVC-ColonDB', 'ETIS-LaribPolypDB']:

        ##### put data_path here #####
        data_path = './dataset/TestDataset/{}'.format(_data_name)
        ##### save_path #####
        save_path = './result_map/PolypPVT_vis/{}/'.format(_data_name)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        image_root = '{}/images/'.format(data_path)
        gt_root = '{}/masks/'.format(data_path)
        num1 = len(os.listdir(gt_root))
        test_loader = test_dataset(image_root, gt_root, 352)

        for i in range(num1):
            image, gt, name = test_loader.load_data()
            gt = np.asarray(gt, np.float32)
            gt /= (gt.max() + 1e-8)
            image = image.cuda()
            P1,P2 = model(image)
            adp = torch.nn.AdaptiveAvgPool2d((P1.shape[-1]))
            
            print("P1 shape:",P1.shape, "P2 shape:",P2.shape)
            # res = F.upsample(P1+P2, size=gt.shape, mode='bilinear', align_corners=False)
            res = adp(P1 + torch.transpose(P1, 1,2))
            tmp = P1 + torch.transpose(P1, 1,2)
            print("symmetrical structure:",tmp.shape)
            print(res.shape)
            res = res.sigmoid().data.cpu().numpy().squeeze()
            # print(res.shape)
            out = []
            for i in range(10):
                res_img = (res[i] - res[i].min()) / (res[i].max() - res[i].min() + 1e-8)
                out.append(res_img)
            # res = (res - res.min()) / (res.max() - res.min() + 1e-8)
            
            out_img = np.concatenate(out, axis = 1)
            cv2.imwrite(save_path+name, out_img*255)
        print(_data_name, 'Finish!')
