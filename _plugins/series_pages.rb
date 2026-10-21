# frozen_string_literal: true

# 按文章 front matter 的 series / series_order 生成系列目录：
#   /blog/series/
#   /blog/series/<slug>/
# 并把上一篇、下一篇写回文章，供 post 布局使用。
# 可选的 _data/series.yml 提供标题与简介；没有条目时用 slug 作为标题。

module Jekyll
  class SeriesPageGenerator < Generator
    safe true
    priority :low

    def generate(site)
      meta = series_metadata(site)
      grouped = group_posts(site)
      bundles = {}

      ordered_slugs(meta, grouped).each do |slug|
        posts = grouped[slug]
        info = meta[slug] || {}
        title = present(info["title"]) || slug
        description = present(info["description"])
        pdf = "/assets/pdf/#{slug}.pdf"
        permalink = "/blog/series/#{slug}/"

        entries = posts.each_with_index.map do |post, _index|
          {
            "title" => post.data["title"],
            "url" => post.url,
            "date_text" => post.date&.strftime("%Y年%m月%d日"),
            "order" => series_order(post),
            "excerpt" => present(post.data["excerpt"])
          }
        end

        posts.each_with_index do |post, index|
          prev_post = index.positive? ? posts[index - 1] : nil
          next_post = posts[index + 1]
          post.data["series_title"] = title
          post.data["series_description"] = description
          post.data["series_permalink"] = permalink
          post.data["series_pdf"] = pdf
          post.data["series_index"] = index + 1
          post.data["series_total"] = posts.length
          post.data["series_prev_url"] = prev_post&.url
          post.data["series_prev_title"] = prev_post&.data&.dig("title")
          post.data["series_next_url"] = next_post&.url
          post.data["series_next_title"] = next_post&.data&.dig("title")
        end

        bundles[slug] = {
          "slug" => slug,
          "title" => title,
          "description" => description,
          "pdf" => pdf,
          "permalink" => permalink,
          "posts" => entries
        }

        page = PageWithoutAFile.new(site, site.source, File.join("blog/series", slug), "index.html")
        page.data.merge!(
          "layout" => "series",
          "title" => title,
          "series_slug" => slug,
          "series_description" => description,
          "permalink" => permalink
        )
        page.content = ""
        site.pages << page
      end

      site.data["series_bundles"] = bundles
      site.data["series_bundle_list"] = ordered_slugs(meta, grouped).map { |slug| bundles[slug] }

      index = PageWithoutAFile.new(site, site.source, "blog/series", "index.html")
      index.data.merge!(
        "layout" => "series-index",
        "title" => "文章系列",
        "permalink" => "/blog/series/"
      )
      index.content = ""
      site.pages << index
    end

    private

    def series_metadata(site)
      raw = site.data["series"]
      meta = {}
      case raw
      when Array
        raw.each do |item|
          next unless item.is_a?(Hash)

          slug = item["slug"].to_s.strip
          next if slug.empty?

          meta[slug] = item
        end
      when Hash
        raw.each do |slug, item|
          meta[slug.to_s] = item.is_a?(Hash) ? item : {}
        end
      end
      meta
    end

    def group_posts(site)
      grouped = Hash.new { |hash, key| hash[key] = [] }
      site.posts.docs.each do |post|
        slug = post.data["series"].to_s.strip
        next if slug.empty?

        grouped[slug] << post
      end
      grouped.each_value do |posts|
        posts.sort_by! do |post|
          [series_order(post), post.date.to_time, post.basename_without_ext.to_s]
        end
      end
      grouped
    end

    def ordered_slugs(meta, grouped)
      slugs = []
      meta.each_key { |slug| slugs << slug if grouped.key?(slug) }
      (grouped.keys - slugs).sort.each { |slug| slugs << slug }
      slugs
    end

    def series_order(post)
      value = post.data["series_order"]
      return value.to_i if value.is_a?(Numeric) || (value.is_a?(String) && value.match?(/\A-?\d+\z/))

      0
    end

    def present(value)
      text = value.to_s.strip
      text.empty? ? nil : text
    end
  end
end
