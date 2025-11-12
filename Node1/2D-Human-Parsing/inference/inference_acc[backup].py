import os
import os.path as osp
import sys
import time
import timeit
from collections import OrderedDict

import numpy as np
from PIL import Image

import torch
from torch.autograd import Variable
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
def inference(net, img_list, opts):
    start_time = timeit.default_timer()

    # Prepare adjacency matrices on CPU
    adj2_ = torch.from_numpy(graph.cihp2pascal_nlp_adj).float()
    adj2_test = adj2_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 20).transpose(2, 3)

    adj1_ = Variable(torch.from_numpy(graph.preprocess_adj(graph.pascal_graph)).float())
    adj3_test = adj1_.unsqueeze(0).unsqueeze(0).expand(1, 1, 7, 7)

    cihp_adj = graph.preprocess_adj(graph.cihp_graph)
    adj3_ = Variable(torch.from_numpy(cihp_adj).float())
    adj1_test = adj3_.unsqueeze(0).unsqueeze(0).expand(1, 1, 20, 20)

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
        output_path = data['output_path'][0]
        label_output_path = data['label_output_path'][0]

        # Ensure directories exist
        os.makedirs(osp.dirname(output_path), exist_ok=True)
        os.makedirs(osp.dirname(label_output_path), exist_ok=True)

        if osp.exists(output_path) and osp.exists(label_output_path):
            print('Skipping existing output:', output_path)
            continue

        net.eval()
        for iii, sample_batched in enumerate(zip(testloader_list, testloader_flip_list)):
            inputs, labels = sample_batched[0]['image'], sample_batched[0]['label']
            inputs_f, _ = sample_batched[1]['image'], sample_batched[1]['label']

            inputs = torch.cat((inputs, inputs_f), dim=0).to(torch.device('cpu'))
            if iii == 0:
                _, _, h, w = inputs.size()
            inputs = Variable(inputs, requires_grad=False)

            with torch.no_grad():
                outputs = net.forward(inputs, adj1_test, adj3_test, adj2_test)
                outputs = (outputs[0] + flip(flip_cihp(outputs[1]), dim=-1)) / 2
                outputs = outputs.unsqueeze(0)

                if iii > 0:
                    outputs = F.interpolate(outputs, size=(h, w), mode='bilinear', align_corners=True)
                    outputs_final = outputs_final + outputs
                else:
                    outputs_final = outputs.clone()

        # Save visual output
        predictions = torch.max(outputs_final, 1)[1]
        results = predictions.cpu().numpy()
        vis_res = decode_labels(results)
        results = results.astype(np.uint8)

        parsing_im = Image.fromarray(vis_res[0])
        parsing_im.save(output_path)
        label_parsing = Image.fromarray(results[0, :, :], 'L')
        label_parsing.save(label_output_path)

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

    # Load model on CPU
    net = deeplab_xception_transfer.deeplab_xception_transfer_projection_v3v5_more_savemem(
        n_classes=20, os=16, hidden_layers=128, source_classes=7
    )

    if opts.loadmodel:
        checkpoint = torch.load(opts.loadmodel, map_location=torch.device('cpu'))
        net.load_source_model(checkpoint)
        print('Loaded model:', opts.loadmodel)
    else:
        raise RuntimeError('No model provided!')

    net.to(torch.device('cpu'))  # Force CPU mode

    if not os.path.exists(opts.output_dir):
        os.makedirs(opts.output_dir)

    # Load image list
    with open(osp.join(opts.data_root, opts.img_list)) as f:
        imgs = f.readlines()

    inference(net=net, img_list=imgs, opts=opts)
