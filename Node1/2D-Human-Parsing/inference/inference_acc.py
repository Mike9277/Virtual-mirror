#!/usr/bin/env python3

import os
import os.path as osp
import sys
import time
import timeit
from collections import OrderedDict

import numpy as np
from PIL import Image

import torch
import torch.nn.functional as F

sys.path.append('..')
# Custom includes
from dataloaders import custom_transforms as tr
from networks import deeplab_xception_transfer, graph
from inference_dataset import get_infernce_dataloader

# ---------------- label colors ----------------
label_colours = [
    (0,0,0), (128,0,0), (255,0,0), (0,85,0), (170,0,51), 
    (255,85,0), (0,0,85), (0,119,221), (85,85,0), (0,85,85), 
    (85,51,0), (52,86,128), (0,128,0), (0,0,255), (51,170,221),
    (0,255,255), (85,255,170), (170,255,85), (255,255,0), (255,170,0)
]

# ---------------- helper functions ----------------
def flip(x, dim):
    indices = [slice(None)] * x.dim()
    indices[dim] = torch.arange(x.size(dim)-1, -1, -1, dtype=torch.long, device=x.device)
    return x[tuple(indices)]

def flip_cihp(tail_list):
    tail_list_rev = [None]*20
    for xx in range(14):
        tail_list_rev[xx] = tail_list[xx].unsqueeze(0)
    tail_list_rev[14] = tail_list[15].unsqueeze(0)
    tail_list_rev[15] = tail_list[14].unsqueeze(0)
    tail_list_rev[16] = tail_list[17].unsqueeze(0)
    tail_list_rev[17] = tail_list[16].unsqueeze(0)
    tail_list_rev[18] = tail_list[19].unsqueeze(0)
    tail_list_rev[19] = tail_list[18].unsqueeze(0)
    return torch.cat(tail_list_rev, dim=0)

def decode_labels(mask, num_images=1, num_classes=20):
    n, h, w = mask.shape
    outputs = np.zeros((num_images, h, w, 3), dtype=np.uint8)
    for i in range(num_images):
        img = Image.new('RGB', (w, h))
        pixels = img.load()
        for j_ in range(h):
            for k_ in range(w):
                cls = mask[i, j_, k_]
                if cls < num_classes:
                    pixels[k_, j_] = label_colours[cls]
        outputs[i] = np.array(img)
    return outputs

# ---------------- inference ----------------
def inference_fast(net, imgs, opts):
    start_time = timeit.default_timer()

    # Automatic device selection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Inference device: {device}")

    # Precompute adjacency matrices
    adj2_test = torch.from_numpy(graph.cihp2pascal_nlp_adj).float().unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 20).transpose(2, 3).to(device)
    adj3_test = torch.from_numpy(graph.preprocess_adj(graph.pascal_graph)).float().unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 7).to(device)
    adj1_test = torch.from_numpy(graph.preprocess_adj(graph.cihp_graph)).float().unsqueeze(0).unsqueeze(0).expand(1, 1, 20, 20).to(device)

    # Output directory
    output_dir = osp.join(opts.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    net.eval()
    net.to(device)

    inference_dataloader = get_infernce_dataloader(opts)
    total = len(inference_dataloader)
    showFreq = 50
    sstime = time.time()

    for i_batch, data in enumerate(inference_dataloader):
        if i_batch % showFreq == 0 and i_batch != 0:
            exp_time = time.time() - sstime
            avg_time = exp_time / i_batch
            print(f'[{i_batch}/{total}] Total time: {exp_time:.2f}s, Avg: {avg_time:.2f}s')

        testloader_list = data['testloader_list']
        testloader_flip_list = data['testloader_flip_list']

        # Extract filename and generates output filenames.
        src_img_path = imgs[i_batch].strip()
        base_name = osp.splitext(osp.basename(src_img_path))[0]

        output_path = osp.join(output_dir, f"{base_name}_vis.png")
        label_output_path = osp.join(output_dir, f"{base_name}_label.png")

        # Skip già elaborati
        if osp.exists(output_path) and osp.exists(label_output_path):
            print('Skipping existing output:', output_path)
            continue

        outputs_final = None

        for iii, sample_batched in enumerate(zip(testloader_list, testloader_flip_list)):
            inputs = sample_batched[0]['image'].to(device)
            inputs_f = sample_batched[1]['image'].to(device)

            inputs_cat = torch.cat((inputs, inputs_f), dim=0)
            with torch.no_grad():
                outputs = net(inputs_cat, adj1_test, adj3_test, adj2_test)
                outputs = (outputs[0] + flip(flip_cihp(outputs[1]), dim=-1)) / 2

                # Output has to be 4D for f.intermpolate
                if outputs.dim() == 3:
                    outputs = outputs.unsqueeze(0)

                if iii == 0:
                    outputs_final = outputs
                else:
                    outputs_final += F.interpolate(outputs, size=outputs_final.shape[2:], mode='bilinear', align_corners=True)

        # Media finale
        outputs_final /= len(testloader_list)
        predictions = torch.argmax(outputs_final, dim=1)
        results = predictions.cpu().numpy().astype(np.uint8)
        vis_res = decode_labels(results)

        # Salva risultati
        Image.fromarray(vis_res[0]).save(output_path)
        Image.fromarray(results[0, :, :], 'L').save(label_output_path)

    print(f"Total inference time: {timeit.default_timer() - start_time:.2f}s")

# ---------------- main ----------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--loadmodel', default='', type=str)
    parser.add_argument('--img_list', default='', type=str)
    parser.add_argument('--output_dir', default='', type=str)
    parser.add_argument('--data_root', default='', type=str)
    parser.add_argument('--phase', default='train', type=str)
    opts = parser.parse_args()

    # Load model
    net = deeplab_xception_transfer.deeplab_xception_transfer_projection_v3v5_more_savemem(
        n_classes=20, os=16, hidden_layers=128, source_classes=7
    )

    if opts.loadmodel:
        checkpoint = torch.load(opts.loadmodel, map_location=torch.device('cpu'))
        net.load_source_model(checkpoint)
        print('Loaded model:', opts.loadmodel)
    else:
        raise RuntimeError('No model provided!')

    # Force CPU initially (model sarà trasferito su GPU se disponibile)
    net.to(torch.device('cpu'))

    if not os.path.exists(opts.output_dir):
        os.makedirs(opts.output_dir)

    # Load image list
    with open(osp.join(opts.data_root, opts.img_list)) as f:
        imgs = f.readlines()

    # Run inference
    inference_fast(net=net, imgs=imgs, opts=opts)
