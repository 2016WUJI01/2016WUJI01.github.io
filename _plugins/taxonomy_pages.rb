# frozen_string_literal: true

# 根据文章 front matter 中的 categories / tags 自动生成归档页：
#   /blog/categories/<slug>/
#   /blog/tags/<slug>/

module Jekyll
  class TaxonomyGenerator < Generator
    safe true
    priority :low

    def generate(site)
      generate_pages(site, site.categories, "category", "blog/categories")
      generate_pages(site, site.tags, "tag", "blog/tags")
    end

    private

    def generate_pages(site, taxonomies, type, dir)
      taxonomies.each do |name, _posts|
        slug = Jekyll::Utils.slugify(name.to_s)
        next if slug.nil? || slug.empty?

        page = PageWithoutAFile.new(site, site.source, File.join(dir, slug), "index.html")
        page.data.merge!(
          "layout" => "taxonomy",
          "title" => name,
          "taxonomy_name" => name,
          "taxonomy_type" => type,
          "permalink" => "/#{dir}/#{slug}/"
        )
        page.content = ""
        site.pages << page
      end
    end
  end
end
