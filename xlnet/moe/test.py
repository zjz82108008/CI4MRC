import torch
# import pymetis

# model = torch.load('../output_squad_xlnet_large/split/param_split/transformer.layer.0.ff.layer_1.weight')
# print(model)
model = torch.load('../output_squad_xlnet_large/split/gp_split/transformer.layer.22.ff.layer_1.weight')
a = model  #.state_dict()
print(model)
# a = pymetis.part_graph(64, model)