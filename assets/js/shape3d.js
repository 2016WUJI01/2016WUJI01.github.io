/**
 * 将 Markdown 中的 ```shape3d / ```threejs 代码块渲染为可拖动的 3D 场景。
 *
 * 两种写法：
 * 1. JSON 声明：{ "shape": "torus", "color": "#6366f1" }
 * 2. 直接写 JS：可使用 THREE、scene、camera、renderer、controls
 */
(function () {
  var BLOCK_SELECTOR =
    ".language-shape3d, .language-threejs, .language-three, script[type='text/shape3d'], [data-shape3d]";

  var SHAPE_ALIASES = {
    cube: "box",
    box: "box",
    square: "box",
    sphere: "sphere",
    ball: "sphere",
    torus: "torus",
    donut: "torus",
    cone: "cone",
    cylinder: "cylinder",
    tetrahedron: "tetrahedron",
    pyramid: "tetrahedron",
    octahedron: "octahedron",
    icosahedron: "icosahedron",
    dodecahedron: "dodecahedron",
    "torus-knot": "torusKnot",
    torusknot: "torusKnot",
    knot: "torusKnot",
    capsule: "capsule",
  };

  function prefersReducedMotion() {
    return (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function cssVar(name, fallback) {
    var value = getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim();
    return value || fallback;
  }

  function sceneBackground() {
    return cssVar("--color-bg-elevated", "#ffffff");
  }

  function getSourceText(block) {
    if (block.matches("[data-shape3d]")) {
      return block.getAttribute("data-shape3d") || "";
    }
    if (block.tagName === "SCRIPT") {
      return block.textContent || "";
    }
    var code = block.querySelector("code");
    return (code ? code.textContent : block.textContent) || "";
  }

  function parseSource(text) {
    var trimmed = text.trim();
    if (!trimmed) {
      return { mode: "json", data: { shape: "icosahedron" } };
    }
    if (trimmed.charAt(0) === "{") {
      try {
        return { mode: "json", data: JSON.parse(trimmed) };
      } catch (err) {
        return { mode: "js", code: trimmed, parseError: err };
      }
    }
    return { mode: "js", code: trimmed };
  }

  function toColor(THREE, value, fallback) {
    try {
      return new THREE.Color(value || fallback);
    } catch (err) {
      return new THREE.Color(fallback);
    }
  }

  function createGeometry(THREE, options) {
    var key = String(options.shape || "icosahedron")
      .replace(/[\s_]/g, "")
      .toLowerCase();
    var kind = SHAPE_ALIASES[key] || key;
    var size = Number(options.size) || 1.35;
    var radius = Number(options.radius) || size * 0.62;

    switch (kind) {
      case "box":
        return new THREE.BoxGeometry(
          Number(options.width) || size,
          Number(options.height) || size,
          Number(options.depth) || size
        );
      case "sphere":
        return new THREE.SphereGeometry(radius, 64, 48);
      case "torus":
        return new THREE.TorusGeometry(
          Number(options.radius) || 0.78,
          Number(options.tube) || 0.28,
          32,
          96
        );
      case "cone":
        return new THREE.ConeGeometry(
          Number(options.radius) || 0.72,
          Number(options.length) || Number(options.size) || 1.5,
          48
        );
      case "cylinder":
        return new THREE.CylinderGeometry(
          Number(options.radiusTop) || Number(options.radius) || 0.55,
          Number(options.radiusBottom) || Number(options.radius) || 0.55,
          Number(options.length) || Number(options.size) || 1.4,
          48
        );
      case "tetrahedron":
        return new THREE.TetrahedronGeometry(radius * 1.15);
      case "octahedron":
        return new THREE.OctahedronGeometry(radius);
      case "dodecahedron":
        return new THREE.DodecahedronGeometry(
          radius,
          Number(options.detail) || 0
        );
      case "torusKnot":
        return new THREE.TorusKnotGeometry(
          Number(options.radius) || 0.72,
          Number(options.tube) || 0.24,
          180,
          24
        );
      case "capsule":
        return new THREE.CapsuleGeometry(
          Number(options.radius) || 0.38,
          Number(options.length) || 0.85,
          8,
          24
        );
      case "icosahedron":
      default:
        return new THREE.IcosahedronGeometry(
          radius,
          Number(options.detail) || 0
        );
    }
  }

  function createMaterial(THREE, options) {
    return new THREE.MeshPhysicalMaterial({
      color: toColor(THREE, options.color, "#6366f1"),
      metalness: options.metalness != null ? Number(options.metalness) : 0.28,
      roughness: options.roughness != null ? Number(options.roughness) : 0.32,
      wireframe: Boolean(options.wireframe),
      clearcoat: options.clearcoat != null ? Number(options.clearcoat) : 0.45,
      clearcoatRoughness: 0.28,
    });
  }

  function applyTransform(mesh, options) {
    var pos = options.position || {};
    var rot = options.rotation || {};
    mesh.position.set(
      Number(pos.x) || 0,
      Number(pos.y) || 0,
      Number(pos.z) || 0
    );
    mesh.rotation.set(
      Number(rot.x) || 0,
      Number(rot.y) || 0,
      Number(rot.z) || 0
    );
  }

  var VIEWER_KEYS = { autoRotate: 1, height: 1, background: 1, shapes: 1 };

  function shapeItemsFrom(data) {
    if (Array.isArray(data.shapes) && data.shapes.length) {
      return data.shapes;
    }
    var item = {};
    Object.keys(data).forEach(function (key) {
      if (!VIEWER_KEYS[key]) item[key] = data[key];
    });
    if (!item.shape) item.shape = item.type || "icosahedron";
    return [item];
  }

  function addDeclaredShapes(THREE, scene, data) {
    shapeItemsFrom(data).forEach(function (item) {
      var mesh = new THREE.Mesh(
        createGeometry(THREE, item),
        createMaterial(THREE, item)
      );
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      applyTransform(mesh, item);
      scene.add(mesh);
    });
  }

  function setupLights(THREE, scene) {
    var ambient = new THREE.AmbientLight(0xffffff, 0.55);
    var hemi = new THREE.HemisphereLight(0xdbeafe, 0x1e293b, 0.55);
    var key = new THREE.DirectionalLight(0xffffff, 1.15);
    key.position.set(3.2, 5.2, 4.2);
    var fill = new THREE.DirectionalLight(0x93c5fd, 0.35);
    fill.position.set(-4, 1.2, -2);
    scene.add(ambient, hemi, key, fill);
  }

  function showError(viewer, message) {
    viewer.classList.add("is-error");
    viewer.innerHTML =
      '<p class="shape3d-error">3D 代码块渲染失败：' +
      String(message).replace(/[<>&]/g, function (ch) {
        return ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" })[ch];
      }) +
      "</p>";
  }

  function runUserScript(THREE, scene, camera, renderer, controls, code) {
    var fn = new Function(
      "THREE",
      "scene",
      "camera",
      "renderer",
      "controls",
      '"use strict";\n' + code + "\n"
    );
    var result = fn(THREE, scene, camera, renderer, controls);
    if (result && result.isObject3D) {
      scene.add(result);
    }
  }

  function mountViewer(block, THREE, OrbitControls) {
    var source = parseSource(getSourceText(block));
    var data = source.mode === "json" ? source.data || {} : {};

    var viewer = document.createElement("div");
    viewer.className = "shape3d-viewer";
    viewer.setAttribute("role", "img");
    viewer.setAttribute("aria-label", "可拖动的 3D 形状，拖动旋转，滚轮缩放");

    var canvasHost = document.createElement("div");
    canvasHost.className = "shape3d-canvas";
    viewer.appendChild(canvasHost);

    var hint = document.createElement("div");
    hint.className = "shape3d-hint";
    hint.textContent =
      source.mode === "js" ? "JS · 拖动旋转 · 滚轮缩放" : "拖动旋转 · 滚轮缩放";
    viewer.appendChild(hint);

    if (block.matches("[data-shape3d]")) {
      block.appendChild(viewer);
    } else {
      block.insertAdjacentElement("afterend", viewer);
      block.hidden = true;
      block.setAttribute("data-shape3d-mounted", "true");
    }

    var height = Number(data.height) || 380;
    viewer.style.height = height + "px";

    var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    canvasHost.appendChild(renderer.domElement);

    var scene = new THREE.Scene();
    scene.background = toColor(THREE, data.background, sceneBackground());

    var camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(2.6, 1.7, 3.1);

    var controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enablePan = false;
    controls.minDistance = 1.4;
    controls.maxDistance = 10;
    controls.target.set(0, 0, 0);

    setupLights(THREE, scene);

    try {
      if (source.mode === "js") {
        if (source.parseError) {
          throw source.parseError;
        }
        runUserScript(THREE, scene, camera, renderer, controls, source.code);
      } else {
        addDeclaredShapes(THREE, scene, data);
      }
    } catch (err) {
      showError(viewer, err && err.message ? err.message : err);
      return;
    }

    var autoRotate =
      source.mode === "js"
        ? data.autoRotate === true
        : data.autoRotate !== false && !prefersReducedMotion();
    var visible = true;

    function resize() {
      var width = viewer.clientWidth || 1;
      var nextHeight = viewer.clientHeight || height;
      camera.aspect = width / nextHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(width, nextHeight, false);
    }

    function syncTheme() {
      if (!data.background) {
        scene.background = toColor(THREE, null, sceneBackground());
      }
    }

    function tick() {
      requestAnimationFrame(tick);
      if (!visible) return;
      if (autoRotate) {
        scene.traverse(function (obj) {
          if (obj.isMesh) {
            obj.rotation.y += 0.006;
            obj.rotation.x += 0.0015;
          }
        });
      }
      controls.update();
      renderer.render(scene, camera);
    }

    resize();
    tick();

    if (typeof ResizeObserver === "function") {
      new ResizeObserver(resize).observe(viewer);
    } else {
      window.addEventListener("resize", resize);
    }

    if (typeof IntersectionObserver === "function") {
      new IntersectionObserver(function (entries) {
        visible = Boolean(entries[0] && entries[0].isIntersecting);
      }).observe(viewer);
    }

    var themeObserver = new MutationObserver(syncTheme);
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
  }

  function collectBlocks() {
    return Array.prototype.slice.call(document.querySelectorAll(BLOCK_SELECTOR)).filter(
      function (block) {
        return !block.hasAttribute("data-shape3d-mounted");
      }
    );
  }

  async function boot() {
    var blocks = collectBlocks();
    if (!blocks.length) return;

    try {
      var THREE = await import("three");
      var controlsMod = await import("three/addons/controls/OrbitControls.js");
      blocks.forEach(function (block) {
        mountViewer(block, THREE, controlsMod.OrbitControls);
      });
    } catch (err) {
      collectBlocks().forEach(function (block) {
        var fallback = document.createElement("div");
        fallback.className = "shape3d-viewer is-error";
        fallback.innerHTML =
          '<p class="shape3d-error">无法加载 Three.js：' +
          String(err && err.message ? err.message : err) +
          "</p>";
        block.insertAdjacentElement("afterend", fallback);
        block.hidden = true;
        block.setAttribute("data-shape3d-mounted", "true");
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
