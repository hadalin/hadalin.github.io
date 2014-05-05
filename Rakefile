require 'html-proofer'

task :test do
  sh "bundle exec jekyll build"
  options = {
      :assume_extension => true,
      :check_html => true,
      :report_invalid_tags => true,
      :report_mismatched_tags => true,
      :report_missing_doctype => true,
      :check_opengraph => true,
      :check_favicon => true,
      :http_status_ignore => [503, 999],
      :url_ignore => [/^https:\/\/twitter.com.*$/],
      :typhoeus => {
        :ssl_verifypeer => false,
        :ssl_verifyhost => 0,
      }
    }
  HTMLProofer.check_directory("./_site", options).run
end
