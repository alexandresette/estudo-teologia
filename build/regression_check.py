from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://localhost:8801/index.html")
    page.wait_for_timeout(500)

    for book_id, corridor in [("exegese", "teologia"), ("tbnt", "teologia"), ("grego", "teologia"), ("homiletica", "teologia"), ("missio", "teologia"), ("arbi", "teologia"), ("tcc1", "teologia"), ("exnote", "teologia")]:
        page.click(f'.corridor-zone[data-corridor="{corridor}"]')
        page.wait_for_timeout(500)
        page.click(f'.bcover[data-id="{book_id}"]')
        page.wait_for_timeout(1200)
        counter = page.eval_on_selector('#counter', 'el => el.textContent')
        print(f"{book_id}: opened at {counter}")
        for _ in range(5):
            page.click('#flipNext')
            page.wait_for_timeout(80)
        counter2 = page.eval_on_selector('#counter', 'el => el.textContent')
        print(f"{book_id}: after 5 flips {counter2}")
        page.click('#backBtn')
        page.wait_for_timeout(400)
        page.click('.corridor-zone[data-corridor="livros"]') if False else None
        # go back to landing corridor view for next book
        page.goto("http://localhost:8801/index.html")
        page.wait_for_timeout(500)

    # also spot-check the Livros/Secreto corridors still render (unrelated books untouched)
    page.click('.corridor-zone[data-corridor="secreto"]')
    page.wait_for_timeout(500)
    n = page.eval_on_selector_all('.bcover', 'els => els.length')
    print("secreto corridor bcover count:", n)

    print("page errors:", errs)
    browser.close()
