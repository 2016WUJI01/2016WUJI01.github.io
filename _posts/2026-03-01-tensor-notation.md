---
layout: post
title: "张量记号：阶、模与元素"
date: 2026-03-01
categories: [研究笔记]
tags: [张量, 机器学习]
series: demo-tensor-notes
series_order: 1
excerpt: "用阶、模和元素下标把向量、矩阵和更高阶数组写成同一套记号，并给出 Frobenius 范数。"
---

向量是一阶数组，矩阵是二阶数组。把这个说法再推进一步，阶为 $$N$$ 的数组就叫 $$N$$ 阶张量。这篇只固定后面两篇要用的记号；模式展开见[《模式展开：把张量写成矩阵》](/blog/2026/03/tensor-matricization/)，用秩一张量之和去逼近见[《CP 分解》](/blog/2026/03/cp-decomposition/)。

## 阶与模

实值三阶张量写成

$$
\mathcal{X} \in \mathbb{R}^{I \times J \times K}.
$$

三个维度分别叫 mode-1、mode-2 和 mode-3，长度是 $$I$$、$$J$$ 和 $$K$$。一般地，$$N$$ 阶张量 $$\mathcal{X}$$ 的第 $$n$$ 模长度为 $$I_n$$。元素用下标一次写全：$$\mathcal{X}_{i_1 i_2 \ldots i_N}$$。三阶时就是 $$\mathcal{X}_{ijk}$$。

| 阶 | 常见称呼 | 本文记号 |
| --- | --- | --- |
| 1 | 向量 | 粗体小写 |
| 2 | 矩阵 | 粗体大写 |
| 3 及以上 | 张量 | 花体 |

calligraphy 只用于张量本身，例如 $$\mathcal{X}$$；沿着某一个模切出来的向量仍然用粗体，例如第 $$k$$ 张正面切片里的列 $$\mathbf{x}_{:jk}$$。

## 范数

后面比较近似误差时用 Frobenius 范数。它只是把每个元素的平方加起来再开方：

$$
\| \mathcal{X} \|_F = \sqrt{\sum_{i=1}^{I} \sum_{j=1}^{J} \sum_{k=1}^{K} \mathcal{X}_{ijk}^{2}}.
$$

行内也可以直接写 $$\|\mathcal{X}\|_F$$。这个定义不依赖基的选择，所以下一篇把 $$\mathcal{X}$$ 摊成矩阵之后，矩阵的 Frobenius 范数和原来相同。
