from tempfile import template
import utils
import numpy as np
import torch
import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--model_path', type=str, default='results/t5-base/ckpt.bin', help='path to the model checkpoint')
parser.add_argument('--res_path', type=str, default='results/t5-base/', help='path to store the results of moefication')
parser.add_argument('--num-layer', type=int, default=24, help='number of layers')
parser.add_argument('--num-expert', type=int, default=64, help='number of experts')
parser.add_argument('--templates', type=str, default='encoder.blocks.{}.ff.dense_relu_dense.wi.weight,decoder.blocks.{}.ff.dense_relu_dense.wi.weight', help='weight names of the first linear layer in each FFN (use comma to separate multiple templates)')

args = parser.parse_args()

args.model_path = '../output_squad_bert_large/pytorch_model.bin'
args.res_path = '../output_squad_bert_large/split/'
args.templates = 'bert.encoder.layer.{}.intermediate.dense.weight'

config = utils.ModelConfig(args.model_path, args.res_path, split_num=args.num_expert)

templates = args.templates.split(',')
for template in templates:
    for i in range(args.num_layer):
        if i in range(16):
            continue
        # center = utils.MLPCenter(config, template, '{}/gp_split/{}.model'.format(args.res_path, template.format(i)))
        center = utils.MLPCenter(config, template, '{}/gp_split/{}'.format(args.res_path, template.format(i)))
        center.cal_center()
