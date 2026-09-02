---
layout: post
title: "在 Markdown 里嵌入可拖动的 3D 形状"
date: 2026-09-02
---

博客文章仍然只写 Markdown。只要把围栏代码块的语言写成 `shape3d`（或 `threejs`），页面加载后会用 Three.js 把它变成可拖动、可缩放的 3D 场景。

适合用来展示几何体、论文里的结构示意，或者随手写一段 JS 搭一个小场景。

## 声明式 JSON（最常用）

不写渲染代码，只描述形状：

```shape3d
{
  "shape": "icosahedron",
  "color": "#2563eb",
  "metalness": 0.35,
  "roughness": 0.28
}
```

拖动可以旋转，滚轮可以缩放。下面这个环面把自动旋转关了，方便自己转着看：

```shape3d
{
  "shape": "torus",
  "color": "#0d9488",
  "autoRotate": false,
  "height": 340
}
```

也可以一次放多个物体：

```shape3d
{
  "autoRotate": true,
  "height": 360,
  "shapes": [
    { "shape": "cube", "color": "#2563eb", "size": 0.9, "position": { "x": -1.35, "y": 0, "z": 0 } },
    { "shape": "sphere", "color": "#059669", "radius": 0.55, "position": { "x": 0, "y": 0, "z": 0 } },
    { "shape": "cone", "color": "#d97706", "radius": 0.42, "length": 1.1, "position": { "x": 1.35, "y": 0, "z": 0 } }
  ]
}
```

## 直接写 JS

代码块里不是 JSON 时，会当作 JavaScript 执行。可以使用 `THREE`、`scene`、`camera`、`renderer`、`controls`：

```shape3d
const geometry = new THREE.TorusKnotGeometry(0.72, 0.24, 180, 24);
const material = new THREE.MeshPhysicalMaterial({
  color: 0x7c3aed,
  metalness: 0.45,
  roughness: 0.22,
  clearcoat: 0.7
});
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

返回一个 `THREE.Object3D` 也会被自动加进场景。

## 写法说明

JSON 字段：

- `shape`：`cube` / `sphere` / `torus` / `cone` / `cylinder` / `tetrahedron` / `octahedron` / `icosahedron` / `dodecahedron` / `torusKnot` / `capsule`
- `color`：CSS 颜色，如 `"#2563eb"`
- `wireframe`、`metalness`、`roughness`、`autoRotate`
- `height`：画布高度（像素）
- `shapes`：多个物体；每个可带 `position`、`rotation`

文章里这样写即可：

````markdown
```shape3d
{ "shape": "cube", "color": "#2563eb" }
```
````

JS 代码块只应写你自己维护的内容，不要粘贴不可信脚本。
