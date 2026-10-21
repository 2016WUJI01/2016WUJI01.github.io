---
layout: post
title: "模式展开：把张量写成矩阵"
date: 2026-03-02
categories: [研究笔记]
tags: [张量, 机器学习]
series: demo-tensor-notes
series_order: 2
excerpt: "模式-n 展开把张量排成矩阵。三阶张量的 mode-1 展开是一个具体、可核对的下标公式。"
---

[上一篇](/blog/2026/03/tensor-notation/)把三阶张量记成 $$\mathcal{X} \in \mathbb{R}^{I \times J \times K}$$。很多算法只接受矩阵，所以要沿某一个模把元素重新排开。排出来的矩阵叫模式展开（mode-n unfolding），也叫 matricization。

## 形状

沿第 $$n$$ 模展开得到

$$
\mathbf{X}_{(n)} \in \mathbb{R}^{I_n \times \prod_{m \neq n} I_m}.
$$

行数永远是被展开的那一模的长度。对其余模，列下标按约定的顺序把多下标合成一个整数。三阶张量的 mode-1 展开是 $$\mathbf{X}_{(1)} \in \mathbb{R}^{I \times JK}$$。

## 下标怎么对

采用列优先、先走最后一模的约定时，元素 $$\mathcal{X}_{ijk}$$ 落到 $$\mathbf{X}_{(1)}$$ 的第 $$i$$ 行、第

$$
p = (j-1)K + k
$$

列。因此

$$
\bigl(\mathbf{X}_{(1)}\bigr)_{ip} = \mathcal{X}_{ijk}, \quad p = (j-1)K + k.
$$

用一个很小的数组可以手算。设 $$I=J=K=2$$，$$\mathcal{X}_{111}=1$$，$$\mathcal{X}_{112}=2$$，$$\mathcal{X}_{121}=3$$，$$\mathcal{X}_{122}=4$$，则第一行是 $$1,2,3,4$$。下面的函数只依赖这个约定：

```python
def unfold_mode1(tensor):
    """把 I x J x K 的张量排成 I x (J*K)，列下标 p = (j-1)*K + k。"""
    i, j, k = tensor.shape
    return tensor.reshape(i, j * k, order="C")
```

`reshape` 之前要确认内存顺序和上面的 $$p$$ 一致；不一致时先转置再展开。展开不改变元素集合，所以

$$
\| \mathbf{X}_{(n)} \|_F = \| \mathcal{X} \|_F.
$$

下一篇的 CP 分解会把因子矩阵和这些展开乘在一起。因子的写法见[《CP 分解》](/blog/2026/03/cp-decomposition/)。
