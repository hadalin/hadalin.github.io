require 'html-proofer'

task :test do
  sh "bundle exec jekyll build --config _config.yml,_config_rake.yml"
  options = {
      :check_html => true,
      :enforce_https => false,
      :report_invalid_tags => true,
      :report_mismatched_tags => true,
      :report_missing_doctype => true,
      :check_opengraph => true,
      :check_favicon => true,
      :ignore_status_codes => [403, 503, 999],
      :url_ignore => [/^https:\/\/twitter.com.*$/, /^https:\/\/web.archive.org.*$/],
      :typhoeus => {
        :ssl_verifypeer => false,
        :ssl_verifyhost => 0,
      }
    }
  HTMLProofer.check_directory("./_site", options).run
end
