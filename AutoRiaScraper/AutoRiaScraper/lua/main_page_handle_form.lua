function select_active_option(splash)
  splash:send_keys("<Down>")
  splash:send_keys("<Enter>")
  splash:wait(1)
end


function main(splash, args)
  -- disables incognito mode to allow some of the browsing data persist between requests
  splash.private_mode_enabled = false
  -- disables images rendering to save network traffic and make rendering faster
  splash.images_enabled = false
  -- disables HTML5 media, including HTML5 video and audio
  splash.html5_media_enabled = false
  -- disables media source extensions API for streaming media
  splash.media_source_enabled = false
  -- disables 2D and 3D graphics to be rendered
  splash.webgl_enabled = false
  -- sets a default timeout for network requests in seconds
  splash.resource_timeout = 10.0

  assert(splash:go(args.url))
  splash:wait(3)

  -- select the type of vehicles to look for
  local carCategory = splash.args.car_category
  local carCategorySelect = splash:select('#at-category')
  carCategorySelect:send_text(carCategory)
  splash:wait(0.3)

  -- select brand of the vehicle (from dynamic select menu)
  local carBrand = splash.args.car_brand
  local carBrandSelect = splash:select('#autocompleteInput-brand-0')
  carBrandSelect:send_text(carBrand)
  splash:wait(1)

  select_active_option(splash)

  -- scroll to the bottom to make 'Search' button visible
  splash:runjs("window.scrollTo(0, document.body.scrollHeight);")

  -- Submitting the form
  local submitFormBtn = splash:select('button > .icon-search')
  submitFormBtn:mouse_click()

  splash:wait(3)
  return splash:html()
end
