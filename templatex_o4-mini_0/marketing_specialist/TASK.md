# The Task

I am a marketing specialist creating personalized email campaigns and dynamic landing pages. I want to blend dynamic content—user names, promo codes, A/B test snippets—and ensure everything is properly escaped in HTML and URL contexts, while being able to preview partials and track performance. This codebase is the heart of my email and landing-page toolkit.

# The Requirements

* `enable_sandbox_mode` : Prevent rogue code from running in designer-provided email templates.  
* `include('header.html')` : Modular email components like headers, footers, and CTA blocks via includes.  
* `cache_template(name)` : Cache popular campaign templates so preview loads are lightning fast.  
* `render_stream(name, context)` : Stream multipart MIME emails without buffering entire message.  
* `escape_html(value)` / `escape_shell(value)` / `escape_json(value)` : Automatic escaping for HTML bodies, URLs, and JSON payloads.  
* `dot_lookup(ctx, 'user.first_name')` : Clean nested access to user profile properties for personalization.  
* `minify_html(output)` : Strip comments and collapse whitespace to reduce email size and avoid spam filters.  
* `default_filter(value, default)` : Provide fallbacks for optional promo codes or dynamic content (`{{ coupon|default('NOCODE') }}`).  
* `add_filter('uppercase', func)` : Custom filters for uppercase text, link tracking, or emoji insertion.  
* `profile_render(name)` : Monitor render times to A/B test partial performance in live campaigns.  
