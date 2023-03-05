function main(splash, args)
    assert(splash:go(args.url))
    while not splash:select(".auto-wrap") do
        splash:wait(0.1)
    end
    return splash:html()
end
