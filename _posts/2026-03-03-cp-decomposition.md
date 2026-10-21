---
layout: post
title: "CP 分解：用秩一张量之和逼近"
date: 2026-03-03
categories: [研究笔记]
tags: [张量, 机器学习]
series: demo-tensor-notes
series_order: 3
excerpt: "CP 把张量写成 R 个秩一张量的和。每个秩一张量是三条向量的外积，权重吸收进因子矩阵。"
---

有了[记号](/blog/2026/03/tensor-notation/)和[模式展开](/blog/2026/03/tensor-matricization/)，可以把一个三阶张量写成少数几个秩一张量的和。这个分解叫 CP（CANDECOMP/PARAFAC）。

## 秩一张量

三条向量 $$\mathbf{a} \in \mathbb{R}^{I}$$、$$\mathbf{b} \in \mathbb{R}^{J}$$、$$\mathbf{c} \in \mathbb{R}^{K}$$ 的外积是一个三阶张量，元素为

$$
(\mathbf{a} \circ \mathbf{b} \circ \mathbf{c})_{ijk} = a_i b_j c_k.
$$

它的秩是 1：任意模式展开都是一个列向量乘一行向量。例如 mode-1 展开就是 $$\mathbf{a}(\mathbf{c} \otimes \mathbf{b})^{\mathsf{T}}$$，这里 $$\otimes$$ 是 Kronecker 积。

## R 项之和

取 $$R$$ 组这样的向量，并给每组一个非负权重 $$\lambda_r$$：

$$
\mathcal{X} \approx \sum_{r=1}^{R} \lambda_r \, \mathbf{a}_r \circ \mathbf{b}_r \circ \mathbf{c}_r.
$$

把 $$\mathbf{a}_r$$ 按列排成 $$I \times R$$ 的因子矩阵 $$\mathbf{A}$$，同样得到 $$\mathbf{B}$$ 和 $$\mathbf{C}$$。权重写成对角阵之后，mode-1 展开变成一次矩阵乘积：

$$
\mathbf{X}_{(1)} \approx \mathbf{A} \, \operatorname{diag}(\boldsymbol{\lambda}) \, (\mathbf{C} \odot \mathbf{B})^{\mathsf{T}},
$$

其中 $$\odot$$ 是 Khatri–Rao 积（按列的 Kronecker 积）。$$\boldsymbol{\lambda}$$ 的第 $$r$$ 个分量就是 $$\lambda_r$$。

实际拟合时最小化 $$\| \mathcal{X} - \hat{\mathcal{X}} \|_F$$。$$R$$ 是这个系列里唯一需要事先选定的整数：它同时决定三块因子矩阵的列数。
