---
layout: default
title: 关于
---

<div class="about-section">
  <h2>个人简介</h2>
  <div class="bio">
    {{ site.data.personal.bio | markdownify }}
  </div>

  {% if site.data.personal.education %}
  <h2>教育背景</h2>
  <ul class="education-list">
    {% for edu in site.data.personal.education %}
    <li>
      <div class="degree">{{ edu.degree }} - {{ edu.field }}</div>
      <div class="institution">{{ edu.institution }}</div>
      <div class="period">{{ edu.year }}</div>
    </li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if site.data.personal.experience %}
  <h2>工作经历</h2>
  <ul class="experience-list">
    {% for exp in site.data.personal.experience %}
    <li>
      <div class="position">{{ exp.position }}</div>
      <div class="institution">
        {% if exp.institution %}
        {{ exp.institution }}
        {% elsif exp.company %}
        {{ exp.company }}
        {% endif %}
      </div>
      <div class="period">{{ exp.period }}</div>
      {% if exp.description %}
      <div class="description">{{ exp.description }}</div>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if site.data.personal.research_areas %}
  <h2>研究领域</h2>
  <ul>
    {% for area in site.data.personal.research_areas %}
    <li>{{ area }}</li>
    {% endfor %}
  </ul>
  {% endif %}
</div>

