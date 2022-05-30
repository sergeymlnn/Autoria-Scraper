function focus(sel)
    splash:select(sel):focus()
end


function main(splash, args)
    assert(splash:go(args.url))
    while not splash:select(".footer-form") do
        splash:wait(0.1)
    end
    local carCategory = splash.args.car_category -- 'Причепи'
    local carCategorySelect = splash:select('#categories')
    carCategorySelect:send_text(carCategory)
    assert(splash:wait(0.2))
    splash:select('.footer-form > button'):mouse_click()
    assert(splash:wait(2))
    return splash:html()
end
