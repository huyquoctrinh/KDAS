import torch
from torch import nn
from lib.pvt import PolypPVT, PolypPVTtiny

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

model = PolypPVTtiny()
count = count_parameters(model)
print (count)