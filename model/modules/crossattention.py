import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import os


def save_atten_vis(attn,base_filename):
    filename = base_filename
    count = 1
    filename = f"{base_filename}_{count}"       
    plt.figure(figsize=(15, 12))
    plt.imshow(attn, cmap='viridis', interpolation='nearest')
# 添加颜色条
    plt.colorbar()
# 设置坐标轴标签等
    plt.title(f'Attention Matrix Visualization')
# 显示可视化结果
    while os.path.exists(filename+".png"):
        count += 1
        filename = f"{base_filename}_{count}"
    plt.savefig(filename+'.png')
    plt.close()

def save_atten_data(attn,base_filename):
    filename = base_filename
    count = 1
    filename = f"{base_filename}_{count}"       

    while os.path.exists(filename+".pt"):
        count += 1
        filename = f"{base_filename}_{count}"

    torch.save(attn,filename+'.pt')

class CrossAttention(nn.Module):

    def __init__(self,dim_in,dim_out,num_heads = 8,qkv_bias = False,qkv_scale = None,attn_drop=0.,proj_drop=0.,
                 mode = 'temporal',back_att = None):
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim_in // num_heads
        self.scale = qkv_scale or head_dim**(-0.5)
        self.wq = nn.Linear(dim_in,dim_in,bias=qkv_bias)
        self.wk = nn.Linear(dim_in,dim_in,bias=qkv_bias)
        self.wv = nn.Linear(dim_in,dim_in,bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim_in,dim_out)
        self.proj_drop = nn.Dropout(proj_drop)
        self.mode = mode
        self.back_att = back_att

    def forward(self,q,kv):
        #batch_size temporal_frame_num num_joints feature_dim
        b , t , j , d = q.shape
        t_sup = kv.shape[1]
        q = self.wq(q).reshape(b,t,j,self.num_heads,d//self.num_heads).permute(0,3,2,1,4)
        k = self.wk(kv).reshape(b,t_sup,j,self.num_heads,d//self.num_heads).permute(0,3,2,1,4)
        v = self.wv(kv).reshape(b,t_sup,j,self.num_heads,d//self.num_heads).permute(0,3,2,1,4)

        attn = (q @ k.transpose(-2,-1))*self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        out = attn@v  # b h j t c
        out = out.permute(0,3,2,1,4).reshape(b,t,j,d)
        out = self.proj(out)
        out = self.proj_drop(out)
        if self.back_att:
            return attn,out
        else:
            return out



# x = torch.ones((16,9,17,256))
# kv = torch.ones((16,18,17,256))

# net = CrossAttention(dim_in=256,dim_out=256,head_num=8)

# out = net(x,kv)
