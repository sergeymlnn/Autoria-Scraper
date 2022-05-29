function main(splash, args)
    assert(splash:go(args.url))
    assert(splash:wait(0.5))
    assert(splash:runjs("window.scrollTo(0, document.body.scrollHeight);"))
    while not splash:select("#searchPagination") do
        splash:wait(0.1)
    end
    return splash:html()
end
