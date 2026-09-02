---
layout: default
title: 关于
permalink: /about/
---

<div class="container">
  {% include page-header.html title="关于我" subtitle=site.data.personal.affiliation %}

  <div class="about-section">
    <div class="about-block">
      <h2 class="about-block-title">个人简介</h2>
      <div class="about-bio">{{ site.data.personal.bio | markdownify }}</div>
    </div>

    {% if site.data.personal.education %}
      <div class="about-block">
        <h2 class="about-block-title">教育背景</h2>
        <ul class="timeline">
          {% for edu in site.data.personal.education %}
            {% if edu.degree != "" %}
              <li class="timeline-item">
                <div class="timeline-degree">{{ edu.degree }} · {{ edu.field }}</div>
                <div class="timeline-institution">{{ edu.institution }}</div>
                <div class="timeline-period">{{ edu.year }}</div>
              </li>
            {% endif %}
          {% endfor %}
        </ul>
      </div>
    {% endif %}

    {% if site.data.personal.experience %}
      {% assign has_experience = false %}
      {% for exp in site.data.personal.experience %}
        {% if exp.position != "" %}
          {% assign has_experience = true %}
        {% endif %}
      {% endfor %}
      {% if has_experience %}
        <div class="about-block">
          <h2 class="about-block-title">工作经历</h2>
          <ul class="timeline">
            {% for exp in site.data.personal.experience %}
              {% if exp.position != "" %}
                <li class="timeline-item">
                  <div class="timeline-position">{{ exp.position }}</div>
                  <div class="timeline-institution">
                    {% if exp.institution %}{{ exp.institution }}{% elsif exp.company %}{{ exp.company }}{% endif %}
                  </div>
                  <div class="timeline-period">{{ exp.period }}</div>
                  {% if exp.description %}
                    <div class="timeline-description">{{ exp.description }}</div>
                  {% endif %}
                </li>
              {% endif %}
            {% endfor %}
          </ul>
        </div>
      {% endif %}
    {% endif %}

    {% if site.data.personal.research_areas %}
      <div class="about-block">
        <h2 class="about-block-title">研究领域</h2>
        <div class="research-tags">
          {% for area in site.data.personal.research_areas %}
            <span class="tag">{{ area }}</span>
          {% endfor %}
        </div>
      </div>
    {% endif %}
  </div>
</div>
