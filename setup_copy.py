import json
import os
import re

ROOT = r"c:\Users\dejtu\.gemini\antigravity\scratch\devin-tucker-site"

def replace_exact(content, old, new, label=""):
    if old not in content:
        raise ValueError(f"Could not find {label or old!r}")
    return content.replace(old, new, 1)

# 1. Instrument index.html (and copy to devin-tucker-site.html)
with open(os.path.join(ROOT, "index.html"), "r", encoding="utf-8") as f:
    idx = f.read()

idx_replacements = [
    # Header
    ('<span>Devin Tucker</span><small>Videography</small>',
     '<span data-copy="global.brand_name">Devin Tucker</span><small data-copy="global.brand_sub">Videography</small>'),
    ('<a href="#work">Work</a>\n    <a href="#services">Services</a>\n    <a class="ghost" href="#contact">Contact</a>',
     '<a href="#work" data-copy="global.nav_work">Work</a>\n    <a href="#services" data-copy="global.nav_services">Services</a>\n    <a class="ghost" href="#contact" data-copy="global.nav_contact">Contact</a>'),
    # Hero
    ('<h1 class="mask-rv"><span class="mask hello-line" style="--n:0"><span>Hello, I\'m Devin.</span></span><span class="mask tag-line" style="--n:1"><span>Live events and live art, on film.</span></span></h1>',
     '<h1 class="mask-rv"><span class="mask hello-line" style="--n:0"><span data-copy="home.hero.line1">Hello, I\'m Devin.</span></span><span class="mask tag-line" style="--n:1"><span data-copy="home.hero.line2">Live events and live art, on film.</span></span></h1>'),
    ('<p class="lede">A videographer and video editor in Portland, Oregon. I film events, and I make short films with dancers, jugglers, and circus artists.</p>',
     '<p class="lede" data-copy="home.hero.lede">A videographer and video editor in Portland, Oregon. I film events, and I make short films with dancers, jugglers, and circus artists.</p>'),
    ('<a class="btn" href="#work">Watch the reel</a>\n          <a class="textlink" href="#contact">Ask about a project</a>',
     '<a class="btn" href="#work" data-copy="home.hero.cta_primary">Watch the reel</a>\n          <a class="textlink" href="#contact" data-copy="home.hero.cta_secondary">Ask about a project</a>'),
    ('<p class="reel-cap">Showreel placeholder</p>',
     '<p class="reel-cap" data-copy="home.hero.reel_cap">Showreel placeholder</p>'),
    # Doors
    ('<h2 id="doors-h">What I film</h2>',
     '<h2 id="doors-h" data-copy="home.doors.heading">What I film</h2>'),
    ('<h3>Event videography</h3>\n          <p>Galas, conferences, concerts, and celebrations, filmed so you can share them afterward.</p>\n          <span class="door-link">See event films</span>',
     '<h3 data-copy="home.doors.events.title">Event videography</h3>\n          <p data-copy="home.doors.events.body">Galas, conferences, concerts, and celebrations, filmed so you can share them afterward.</p>\n          <span class="door-link" data-copy="home.doors.events.link">See event films</span>'),
    ('<h3>Dance, circus, and performance films</h3>\n          <p>Short films with dancers, jugglers, and circus artists: studio pieces, site-specific work, and performance documentation.</p>\n          <span class="door-link">See art films</span>',
     '<h3 data-copy="home.doors.art.title">Dance, circus, and performance films</h3>\n          <p data-copy="home.doors.art.body">Short films with dancers, jugglers, and circus artists: studio pieces, site-specific work, and performance documentation.</p>\n          <span class="door-link" data-copy="home.doors.art.link">See art films</span>'),
    # Selected Work
    ('<h2 id="work-h">Selected work</h2>',
     '<h2 id="work-h" data-copy="home.work.heading">Selected work</h2>'),
    ('<button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>\n        <button class="chip" type="button" data-filter="events" aria-pressed="false">Events</button>\n        <button class="chip" type="button" data-filter="art" aria-pressed="false">Performance and art</button>',
     '<button class="chip" type="button" data-filter="all" aria-pressed="true" data-copy="home.work.filter_all">All</button>\n        <button class="chip" type="button" data-filter="events" aria-pressed="false" data-copy="home.work.filter_events">Events</button>\n        <button class="chip" type="button" data-filter="art" aria-pressed="false" data-copy="home.work.filter_art">Performance and art</button>'),
    # 6 Tiles
    ('<figcaption><i>Gala highlights</i><span class="tag">Event</span></figcaption>',
     '<figcaption><i data-copy="home.work.tile1.title">Gala highlights</i><span class="tag" data-copy="home.work.tile1.tag">Event</span></figcaption>'),
    ('<figcaption><i>Club passing study</i><span class="tag">Art film</span></figcaption>',
     '<figcaption><i data-copy="home.work.tile2.title">Club passing study</i><span class="tag" data-copy="home.work.tile2.tag">Art film</span></figcaption>'),
    ('<figcaption><i>Conference day</i><span class="tag">Event</span></figcaption>',
     '<figcaption><i data-copy="home.work.tile3.title">Conference day</i><span class="tag" data-copy="home.work.tile3.tag">Event</span></figcaption>'),
    ('<figcaption><i>Silks in the studio</i><span class="tag">Art film</span></figcaption>',
     '<figcaption><i data-copy="home.work.tile4.title">Silks in the studio</i><span class="tag" data-copy="home.work.tile4.tag">Art film</span></figcaption>'),
    ('<figcaption><i>Concert recap</i><span class="tag">Event</span></figcaption>',
     '<figcaption><i data-copy="home.work.tile5.title">Concert recap</i><span class="tag" data-copy="home.work.tile5.tag">Event</span></figcaption>'),
    ('<figcaption><i>Dance on the waterfront</i><span class="tag">Art film</span></figcaption>',
     '<figcaption><i data-copy="home.work.tile6.title">Dance on the waterfront</i><span class="tag" data-copy="home.work.tile6.tag">Art film</span></figcaption>'),
    # 8 Index Items
    ('<i>Gala highlights</i><span>Event</span><span>2026</span><span>2:10</span>',
     '<i data-copy="home.work.idx1.title">Gala highlights</i><span data-copy="home.work.idx1.cat">Event</span><span data-copy="home.work.idx1.year">2026</span><span data-copy="home.work.idx1.dur">2:10</span>'),
    ('<i>Club passing study</i><span>Art film</span><span>2026</span><span>3:40</span>',
     '<i data-copy="home.work.idx2.title">Club passing study</i><span data-copy="home.work.idx2.cat">Art film</span><span data-copy="home.work.idx2.year">2026</span><span data-copy="home.work.idx2.dur">3:40</span>'),
    ('<i>Conference day</i><span>Event</span><span>2026</span><span>1:55</span>',
     '<i data-copy="home.work.idx3.title">Conference day</i><span data-copy="home.work.idx3.cat">Event</span><span data-copy="home.work.idx3.year">2026</span><span data-copy="home.work.idx3.dur">1:55</span>'),
    ('<i>Silks in the studio</i><span>Art film</span><span>2025</span><span>4:05</span>',
     '<i data-copy="home.work.idx4.title">Silks in the studio</i><span data-copy="home.work.idx4.cat">Art film</span><span data-copy="home.work.idx4.year">2025</span><span data-copy="home.work.idx4.dur">4:05</span>'),
    ('<i>Concert recap</i><span>Event</span><span>2025</span><span>1:30</span>',
     '<i data-copy="home.work.idx5.title">Concert recap</i><span data-copy="home.work.idx5.cat">Event</span><span data-copy="home.work.idx5.year">2025</span><span data-copy="home.work.idx5.dur">1:30</span>'),
    ('<i>Dance on the waterfront</i><span>Art film</span><span>2025</span><span>5:20</span>',
     '<i data-copy="home.work.idx6.title">Dance on the waterfront</i><span data-copy="home.work.idx6.cat">Art film</span><span data-copy="home.work.idx6.year">2025</span><span data-copy="home.work.idx6.dur">5:20</span>'),
    ('<i>Opening night</i><span>Event</span><span>2024</span><span>2:35</span>',
     '<i data-copy="home.work.idx7.title">Opening night</i><span data-copy="home.work.idx7.cat">Event</span><span data-copy="home.work.idx7.year">2024</span><span data-copy="home.work.idx7.dur">2:35</span>'),
    ('<i>Rooftop duet</i><span>Art film</span><span>2024</span><span>3:15</span>',
     '<i data-copy="home.work.idx8.title">Rooftop duet</i><span data-copy="home.work.idx8.cat">Art film</span><span data-copy="home.work.idx8.year">2024</span><span data-copy="home.work.idx8.dur">3:15</span>'),
    # Services
    ('<h2 id="services-h">Video services in Portland, Oregon</h2>',
     '<h2 id="services-h" data-copy="home.services.heading">Video services in Portland, Oregon</h2>'),
    ('<div class="svc-row"><h3><a href="event-videography-portland/">Event videography in Portland</a></h3><div class="svc-body"><p>Galas, conferences, concerts, and celebrations. I film the day and edit a highlight film you can share, with longer cuts of speeches or performances when you need them.</p><p class="svc-more"><a class="textlink" href="event-videography-portland/">More about event videography in Portland</a></p></div></div>',
     '<div class="svc-row"><h3><a href="event-videography-portland/" data-copy="home.services.1.title">Event videography in Portland</a></h3><div class="svc-body"><p data-copy="home.services.1.body">Galas, conferences, concerts, and celebrations. I film the day and edit a highlight film you can share, with longer cuts of speeches or performances when you need them.</p><p class="svc-more"><a class="textlink" href="event-videography-portland/" data-copy="home.services.1.link">More about event videography in Portland</a></p></div></div>'),
    ('<div class="svc-row"><h3><a href="dance-and-performance-film-portland/">Dance, circus, and performance films</a></h3><div class="svc-body"><p>Short films made with dancers, jugglers, and circus artists: studio pieces, site-specific work, and documentation of a show. Built from your idea, or from one of mine.</p><p class="svc-more"><a class="textlink" href="dance-and-performance-film-portland/">More about dance, circus, and performance films</a></p></div></div>',
     '<div class="svc-row"><h3><a href="dance-and-performance-film-portland/" data-copy="home.services.2.title">Dance, circus, and performance films</a></h3><div class="svc-body"><p data-copy="home.services.2.body">Short films made with dancers, jugglers, and circus artists: studio pieces, site-specific work, and documentation of a show. Built from your idea, or from one of mine.</p><p class="svc-more"><a class="textlink" href="dance-and-performance-film-portland/" data-copy="home.services.2.link">More about dance, circus, and performance films</a></p></div></div>'),
    ('<div class="svc-row"><h3><a href="video-editing-portland/">Video editing in Portland</a></h3><div class="svc-body"><p>Bring your own footage and I will shape it into a film, a teaser, or a reel.</p><p class="svc-more"><a class="textlink" href="video-editing-portland/">More about video editing in Portland</a></p></div></div>',
     '<div class="svc-row"><h3><a href="video-editing-portland/" data-copy="home.services.3.title">Video editing in Portland</a></h3><div class="svc-body"><p data-copy="home.services.3.body">Bring your own footage and I will shape it into a film, a teaser, or a reel.</p><p class="svc-more"><a class="textlink" href="video-editing-portland/" data-copy="home.services.3.link">More about video editing in Portland</a></p></div></div>'),
    # About & Contact
    ('<h2 id="contact-h">More about me</h2>\n        <p>I film events and make short films about movement, and I edit everything myself.</p>\n        <p>I film events because the best moments are never on the schedule. I film circus and dance because I perform and teach it, so I know when to move closer and when to stay out of the way.</p>\n        <p>I often work with Slipstream Circus Collective, the Portland circus and digital arts collective I founded.</p>\n        <p class="direct">Write directly: <a class="textlink" href="mailto:hello@yourdomain.com">hello@yourdomain.com</a></p>\n        <p class="loc">Portland, Oregon. Vimeo and Instagram links go here.</p>',
     '<h2 id="contact-h" data-copy="home.about.heading">More about me</h2>\n        <p data-copy="home.about.p1">I film events and make short films about movement, and I edit everything myself.</p>\n        <p data-copy="home.about.p2">I film events because the best moments are never on the schedule. I film circus and dance because I perform and teach it, so I know when to move closer and when to stay out of the way.</p>\n        <p data-copy="home.about.p3">I often work with Slipstream Circus Collective, the Portland circus and digital arts collective I founded.</p>\n        <p class="direct"><span data-copy="home.about.direct_label">Write directly:</span> <a class="textlink" data-email-href href="mailto:hello@yourdomain.com" data-copy="global.email">hello@yourdomain.com</a></p>\n        <p class="loc" data-copy="home.about.loc">Portland, Oregon. Vimeo and Instagram links go here.</p>'),
    # Shared Form
    ('<h3 class="form-title">Tell me about your project</h3>\n        <p class="intro">Share the kind of film, what it is for, and when. <span id="book-wrap">Prefer to talk it through first? <a class="textlink" id="book-link" href="https://cal.com/yourname/intro" target="_blank" rel="noopener">Book a short call</a>.</span></p>',
     '<h3 class="form-title" data-copy="form.title">Tell me about your project</h3>\n        <p class="intro"><span data-copy="form.intro">Share the kind of film, what it is for, and when.</span> <span id="book-wrap"><span data-copy="form.book_prompt">Prefer to talk it through first?</span> <a class="textlink" id="book-link" href="https://cal.com/yourname/intro" target="_blank" rel="noopener" data-copy="form.book_link">Book a short call</a>.</span></p>'),
    ('<label for="f-name">Name</label>', '<label for="f-name" data-copy="form.label_name">Name</label>'),
    ('<label for="f-email">Email</label>', '<label for="f-email" data-copy="form.label_email">Email</label>'),
    ('<label for="f-type">Type of project</label>', '<label for="f-type" data-copy="form.label_type">Type of project</label>'),
    ('<label for="f-date">Date or timeframe</label>', '<label for="f-date" data-copy="form.label_date">Date or timeframe</label>'),
    ('<label for="f-msg">What do you have in mind?</label>', '<label for="f-msg" data-copy="form.label_msg">What do you have in mind?</label>'),
    ('<button class="btn" type="submit">Send message</button>', '<button class="btn" type="submit" data-copy="form.submit">Send message</button>'),
    # Footer
    ('<p class="roles">videographer, editor, circus artist, teacher</p>',
     '<p class="roles" data-copy="home.footer.roles">videographer, editor, circus artist, teacher</p>'),
    ('<p class="statusline" id="booking-status">Booking projects for spring 2027</p>',
     '<p class="statusline" id="booking-status" data-copy="home.footer.booking_status">Booking projects for spring 2027</p>'),
    ('<p class="motto">Fatto con cura</p>',
     '<p class="motto" data-copy="home.footer.motto">Fatto con cura</p>'),
]

for old, new in idx_replacements:
    idx = replace_exact(idx, old, new)

if '<script src="/copy-editor.js" defer></script>' not in idx:
    idx = replace_exact(idx, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(idx)
with open(os.path.join(ROOT, "devin-tucker-site.html"), "w", encoding="utf-8") as f:
    f.write(idx)

# 2. Instrument event-videography-portland/index.html
ev_path = os.path.join(ROOT, "event-videography-portland", "index.html")
with open(ev_path, "r", encoding="utf-8") as f:
    ev = f.read()

common_subpage_replacements = [
    ('<span>Devin Tucker</span></a>', '<span data-copy="global.brand_name">Devin Tucker</span></a>'),
    ('<nav class="nav" aria-label="Main"><a href="../index.html#work">Work</a><a href="../index.html#services">Services</a><a class="ghost" href="#contact">Contact</a></nav>',
     '<nav class="nav" aria-label="Main"><a href="../index.html#work" data-copy="global.nav_work">Work</a><a href="../index.html#services" data-copy="global.nav_services">Services</a><a class="ghost" href="#contact" data-copy="global.nav_contact">Contact</a></nav>'),
    ('<h2 id="contact-h">Let\'s talk</h2>', '<h2 id="contact-h" data-copy="subpage.contact_heading">Let\'s talk</h2>'),
    ('<h3 class="form-title">Tell me about your project</h3>\n        <p class="intro">Share the kind of film, what it is for, and when. <span id="book-wrap">Prefer to talk it through first? <a class="textlink" id="book-link" href="https://cal.com/yourname/intro" target="_blank" rel="noopener">Book a short call</a>.</span></p>',
     '<h3 class="form-title" data-copy="form.title">Tell me about your project</h3>\n        <p class="intro"><span data-copy="form.intro">Share the kind of film, what it is for, and when.</span> <span id="book-wrap"><span data-copy="form.book_prompt">Prefer to talk it through first?</span> <a class="textlink" id="book-link" href="https://cal.com/yourname/intro" target="_blank" rel="noopener" data-copy="form.book_link">Book a short call</a>.</span></p>'),
    ('<label for="f-name">Name</label>', '<label for="f-name" data-copy="form.label_name">Name</label>'),
    ('<label for="f-email">Email</label>', '<label for="f-email" data-copy="form.label_email">Email</label>'),
    ('<label for="f-type">Type of project</label>', '<label for="f-type" data-copy="form.label_type">Type of project</label>'),
    ('<label for="f-date">Date or timeframe</label>', '<label for="f-date" data-copy="form.label_date">Date or timeframe</label>'),
    ('<label for="f-msg">What do you have in mind?</label>', '<label for="f-msg" data-copy="form.label_msg">What do you have in mind?</label>'),
    ('<button class="btn" type="submit">Send message</button>', '<button class="btn" type="submit" data-copy="form.submit">Send message</button>'),
]

ev_replacements = common_subpage_replacements + [
    ('<span aria-current="page">Event videography</span>', '<span aria-current="page" data-copy="events.crumb">Event videography</span>'),
    ('<h1 class="mask-rv"><span class="mask" style="--n:0"><span>Event videography in Portland, Oregon</span></span></h1>',
     '<h1 class="mask-rv"><span class="mask" style="--n:0"><span data-copy="events.hero.title">Event videography in Portland, Oregon</span></span></h1>'),
    ('<p class="lede">I film galas, conferences, concerts, and celebrations around Portland, then edit the day into a film you can share. The aim is a film people want to watch twice: the speeches that mattered, the room, and the moments nobody scheduled.</p>',
     '<p class="lede" data-copy="events.hero.lede">I film galas, conferences, concerts, and celebrations around Portland, then edit the day into a film you can share. The aim is a film people want to watch twice: the speeches that mattered, the room, and the moments nobody scheduled.</p>'),
    ('<div class="actions"><a class="btn" href="#contact">Tell me about your event</a><a class="textlink" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener">Book a short call</a></div>',
     '<div class="actions"><a class="btn" href="#contact" data-copy="events.hero.cta">Tell me about your event</a><a class="textlink" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener" data-copy="form.book_link">Book a short call</a></div>'),
    ('<h2>What I film</h2>', '<h2 data-copy="events.what.heading">What I film</h2>'),
    ('<li><strong>Galas and fundraisers.</strong> The room, the speeches, and the people who make the night work.</li>',
     '<li><strong data-copy="events.what.1.title">Galas and fundraisers.</strong> <span data-copy="events.what.1.body">The room, the speeches, and the people who make the night work.</span></li>'),
    ('<li><strong>Conferences and talks.</strong> Speakers, panels, and the conversations in the hallway.</li>',
     '<li><strong data-copy="events.what.2.title">Conferences and talks.</strong> <span data-copy="events.what.2.body">Speakers, panels, and the conversations in the hallway.</span></li>'),
    ('<li><strong>Concerts and live performances.</strong> The stage, the crowd, and the moments between songs.</li>',
     '<li><strong data-copy="events.what.3.title">Concerts and live performances.</strong> <span data-copy="events.what.3.body">The stage, the crowd, and the moments between songs.</span></li>'),
    ('<li><strong>Celebrations.</strong> Parties, openings, and anniversaries worth keeping.</li>',
     '<li><strong data-copy="events.what.4.title">Celebrations.</strong> <span data-copy="events.what.4.body">Parties, openings, and anniversaries worth keeping.</span></li>'),
    ('<h2>How it works</h2>', '<h2 data-copy="events.how.heading">How it works</h2>'),
    ('<p><em>First, we talk.</em> Tell me the date, the place, and what the film is for. We decide what has to be captured and what is a bonus.</p>',
     '<p><em data-copy="events.how.1.title">First, we talk.</em> <span data-copy="events.how.1.body">Tell me the date, the place, and what the film is for. We decide what has to be captured and what is a bonus.</span></p>'),
    ('<p><em>Then I plan the coverage.</em> I ask about the schedule, any speeches or performances, and the venue, and I arrive early to set up.</p>',
     '<p><em data-copy="events.how.2.title">Then I plan the coverage.</em> <span data-copy="events.how.2.body">I ask about the schedule, any speeches or performances, and the venue, and I arrive early to set up.</span></p>'),
    ('<p><em>On the day, I stay out of the way.</em> I film from the edges, avoid interrupting, and work alongside your staff and any photographers.</p>',
     '<p><em data-copy="events.how.3.title">On the day, I stay out of the way.</em> <span data-copy="events.how.3.body">I film from the edges, avoid interrupting, and work alongside your staff and any photographers.</span></p>'),
    ('<p><em>Afterward, I edit.</em> You get a highlight film you can share, and longer cuts of speeches or performances if you ask for them.</p>',
     '<p><em data-copy="events.how.4.title">Afterward, I edit.</em> <span data-copy="events.how.4.body">You get a highlight film you can share, and longer cuts of speeches or performances if you ask for them.</span></p>'),
    ('<h2>What you can ask for</h2>\n    <p>A highlight film for sharing. Full-length cuts of speeches, talks, or performances. Short versions for social media. If you need something else, ask.</p>',
     '<h2 data-copy="events.deliverables.heading">What you can ask for</h2>\n    <p data-copy="events.deliverables.body">A highlight film for sharing. Full-length cuts of speeches, talks, or performances. Short versions for social media. If you need something else, ask.</p>'),
    ('<h2>Filming in Portland</h2>\n    <p>Filming indoors at a private venue is usually settled between you, the venue, and me. Filming on streets, sidewalks, or in city parks is different. The City of Portland\'s Events and Film Office is the place to start for permits, and street and sidewalk permits ask for at least three business days\' notice and proof of insurance. Many venues also ask vendors for a certificate of insurance. If your plans involve any of this, tell me early and we will sort it out together.</p>',
     '<h2 data-copy="events.portland.heading">Filming in Portland</h2>\n    <p data-copy="events.portland.body">Filming indoors at a private venue is usually settled between you, the venue, and me. Filming on streets, sidewalks, or in city parks is different. The City of Portland\'s Events and Film Office is the place to start for permits, and street and sidewalk permits ask for at least three business days\' notice and proof of insurance. Many venues also ask vendors for a certificate of insurance. If your plans involve any of this, tell me early and we will sort it out together.</p>'),
    ('<h2>Questions</h2>\n    <h3>How far ahead should I book?</h3>\n    <p>As early as you can. Dates fill, especially in event season, so write as soon as you have one.</p>\n    <h3>What does it cost?</h3>\n    <p>It depends on how long the event runs, how many places I need to be, and what you want back. Tell me about your day and I will send a quote.</p>\n    <h3>Who owns the film?</h3>\n    <p>We agree this in writing before the event: what you can use the film for, and what I can show in my own portfolio.</p>\n    <h3>Do you work outside Portland?</h3>\n    <p>Mostly in and around Portland. If your event is further away, ask.</p>',
     '<h2 data-copy="events.faq.heading">Questions</h2>\n    <h3 data-copy="events.faq.1.q">How far ahead should I book?</h3>\n    <p data-copy="events.faq.1.a">As early as you can. Dates fill, especially in event season, so write as soon as you have one.</p>\n    <h3 data-copy="events.faq.2.q">What does it cost?</h3>\n    <p data-copy="events.faq.2.a">It depends on how long the event runs, how many places I need to be, and what you want back. Tell me about your day and I will send a quote.</p>\n    <h3 data-copy="events.faq.3.q">Who owns the film?</h3>\n    <p data-copy="events.faq.3.a">We agree this in writing before the event: what you can use the film for, and what I can show in my own portfolio.</p>\n    <h3 data-copy="events.faq.4.q">Do you work outside Portland?</h3>\n    <p data-copy="events.faq.4.a">Mostly in and around Portland. If your event is further away, ask.</p>'),
]

for old, new in ev_replacements:
    ev = replace_exact(ev, old, new)
if '<script src="/copy-editor.js" defer></script>' not in ev:
    ev = replace_exact(ev, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')
with open(ev_path, "w", encoding="utf-8") as f:
    f.write(ev)

# 3. Instrument dance-and-performance-film-portland/index.html
da_path = os.path.join(ROOT, "dance-and-performance-film-portland", "index.html")
with open(da_path, "r", encoding="utf-8") as f:
    da = f.read()

da_replacements = common_subpage_replacements + [
    ('<span aria-current="page">Dance, circus, and performance films</span>', '<span aria-current="page" data-copy="dance.crumb">Dance, circus, and performance films</span>'),
    ('<h1 class="mask-rv"><span class="mask" style="--n:0"><span>Dance, circus, and performance films in Portland</span></span></h1>',
     '<h1 class="mask-rv"><span class="mask" style="--n:0"><span data-copy="dance.hero.title">Dance, circus, and performance films in Portland</span></span></h1>'),
    ('<p class="lede">I make short films with dancers, jugglers, and circus artists: studio pieces, work made for a particular place, and clear documentation of a live show. I am a circus artist and teacher myself, so I know how a routine is built and where the camera should and should not be.</p>',
     '<p class="lede" data-copy="dance.hero.lede">I make short films with dancers, jugglers, and circus artists: studio pieces, work made for a particular place, and clear documentation of a live show. I am a circus artist and teacher myself, so I know how a routine is built and where the camera should and should not be.</p>'),
    ('<div class="actions"><a class="btn" href="#contact">Tell me about your project</a><a class="textlink" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener">Book a short call</a></div>',
     '<div class="actions"><a class="btn" href="#contact" data-copy="dance.hero.cta">Tell me about your project</a><a class="textlink" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener" data-copy="form.book_link">Book a short call</a></div>'),
    ('<h2>What I make</h2>', '<h2 data-copy="dance.what.heading">What I make</h2>'),
    ('<li><strong>Short films.</strong> Made for the screen, usually built together with the artist, in a studio or in a place that suits the work.</li>',
     '<li><strong data-copy="dance.what.1.title">Short films.</strong> <span data-copy="dance.what.1.body">Made for the screen, usually built together with the artist, in a studio or in a place that suits the work.</span></li>'),
    ('<li><strong>Show documentation.</strong> A live performance filmed clearly, so it can be watched, shared, and submitted.</li>',
     '<li><strong data-copy="dance.what.2.title">Show documentation.</strong> <span data-copy="dance.what.2.body">A live performance filmed clearly, so it can be watched, shared, and submitted.</span></li>'),
    ('<li><strong>Reels for artists.</strong> A tight reel for auditions, festivals, venues, and funders.</li>',
     '<li><strong data-copy="dance.what.3.title">Reels for artists.</strong> <span data-copy="dance.what.3.body">A tight reel for auditions, festivals, venues, and funders.</span></li>'),
    ('<li><strong>Collaborations.</strong> Work that grows from an idea, whether it starts with you or with me.</li>',
     '<li><strong data-copy="dance.what.4.title">Collaborations.</strong> <span data-copy="dance.what.4.body">Work that grows from an idea, whether it starts with you or with me.</span></li>'),
    ('<h2>How it works</h2>', '<h2 data-copy="dance.how.heading">How it works</h2>'),
    ('<p><em>We start with the act or the idea.</em> What are you making, who is it for, and where will it be seen?</p>',
     '<p><em data-copy="dance.how.1.title">We start with the act or the idea.</em> <span data-copy="dance.how.1.body">What are you making, who is it for, and where will it be seen?</span></p>'),
    ('<p><em>I plan the film around the performer.</em> Location, light, and what the camera should see, decided together before anyone picks up a camera.</p>',
     '<p><em data-copy="dance.how.2.title">I plan the film around the performer.</em> <span data-copy="dance.how.2.body">Location, light, and what the camera should see, decided together before anyone picks up a camera.</span></p>'),
    ('<p><em>I film with you, not around you.</em> I am a circus artist, juggler, and teacher myself, so I know how a routine is built and when to move closer or stay back.</p>',
     '<p><em data-copy="dance.how.3.title">I film with you, not around you.</em> <span data-copy="dance.how.3.body">I am a circus artist, juggler, and teacher myself, so I know how a routine is built and when to move closer or stay back.</span></p>'),
    ('<p><em>Then I edit.</em> We watch it together and refine it until it is right.</p>',
     '<p><em data-copy="dance.how.4.title">Then I edit.</em> <span data-copy="dance.how.4.body">We watch it together and refine it until it is right.</span></p>'),
    ('<h2>Funding and submissions</h2>\n    <p>A good film is often part of a grant or festival application. Tell me what you are applying to and the format they ask for, and I will cut to it.</p>',
     '<h2 data-copy="dance.funding.heading">Funding and submissions</h2>\n    <p data-copy="dance.funding.body">A good film is often part of a grant or festival application. Tell me what you are applying to and the format they ask for, and I will cut to it.</p>'),
    ('<h2>Where I come from</h2>\n    <p>I perform and teach in Portland, and I often work with Slipstream Circus Collective, the Portland circus and digital arts collective I founded.</p>',
     '<h2 data-copy="dance.origin.heading">Where I come from</h2>\n    <p data-copy="dance.origin.body">I perform and teach in Portland, and I often work with Slipstream Circus Collective, the Portland circus and digital arts collective I founded.</p>'),
    ('<h2>Filming in Portland</h2>\n    <p>Filming in a studio is simple. Filming on streets, sidewalks, or in city parks is different. The City of Portland\'s Events and Film Office is the place to start for permits, and street and sidewalk permits ask for at least three business days\' notice and proof of insurance. Many venues also ask vendors for a certificate of insurance. If your plans involve any of this, tell me early and we will sort it out together.</p>',
     '<h2 data-copy="dance.portland.heading">Filming in Portland</h2>\n    <p data-copy="dance.portland.body">Filming in a studio is simple. Filming on streets, sidewalks, or in city parks is different. The City of Portland\'s Events and Film Office is the place to start for permits, and street and sidewalk permits ask for at least three business days\' notice and proof of insurance. Many venues also ask vendors for a certificate of insurance. If your plans involve any of this, tell me early and we will sort it out together.</p>'),
    ('<h2>Questions</h2>\n    <h3>Do you film live shows?</h3>\n    <p>Yes. I can document a performance so it can be watched afterward, and I will agree the camera positions with you first so I do not get in anyone\'s way.</p>\n    <h3>What if I have never made a film?</h3>\n    <p>That is fine. We start from what you want to show, and I will guide the rest.</p>\n    <h3>What does it cost?</h3>\n    <p>It depends on the length of the piece, the filming days, and the editing. Tell me about the project and I will send a quote.</p>',
     '<h2 data-copy="dance.faq.heading">Questions</h2>\n    <h3 data-copy="dance.faq.1.q">Do you film live shows?</h3>\n    <p data-copy="dance.faq.1.a">Yes. I can document a performance so it can be watched afterward, and I will agree the camera positions with you first so I do not get in anyone\'s way.</p>\n    <h3 data-copy="dance.faq.2.q">What if I have never made a film?</h3>\n    <p data-copy="dance.faq.2.a">That is fine. We start from what you want to show, and I will guide the rest.</p>\n    <h3 data-copy="dance.faq.3.q">What does it cost?</h3>\n    <p data-copy="dance.faq.3.a">It depends on the length of the piece, the filming days, and the editing. Tell me about the project and I will send a quote.</p>'),
]

for old, new in da_replacements:
    da = replace_exact(da, old, new)
if '<script src="/copy-editor.js" defer></script>' not in da:
    da = replace_exact(da, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')
with open(da_path, "w", encoding="utf-8") as f:
    f.write(da)

# 4. Instrument video-editing-portland/index.html
ve_path = os.path.join(ROOT, "video-editing-portland", "index.html")
with open(ve_path, "r", encoding="utf-8") as f:
    ve = f.read()

ve_replacements = common_subpage_replacements + [
    ('<span aria-current="page">Video editing</span>', '<span aria-current="page" data-copy="editing.crumb">Video editing</span>'),
    ('<h1 class="mask-rv"><span class="mask" style="--n:0"><span>Video editing in Portland, Oregon</span></span></h1>',
     '<h1 class="mask-rv"><span class="mask" style="--n:0"><span data-copy="editing.hero.title">Video editing in Portland, Oregon</span></span></h1>'),
    ('<p class="lede">Bring me footage you have shot and I will shape it into a finished film, a teaser, or a reel. I edit events, performances, and promotional videos, and I care about rhythm, sound, and what to leave out.</p>',
     '<p class="lede" data-copy="editing.hero.lede">Bring me footage you have shot and I will shape it into a finished film, a teaser, or a reel. I edit events, performances, and promotional videos, and I care about rhythm, sound, and what to leave out.</p>'),
    ('<div class="actions"><a class="btn" href="#contact">Send me your project</a><a class="textlink" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener">Book a short call</a></div>',
     '<div class="actions"><a class="btn" href="#contact" data-copy="editing.hero.cta">Send me your project</a><a class="textlink" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener" data-copy="form.book_link">Book a short call</a></div>'),
    ('<h2>What I edit</h2>', '<h2 data-copy="editing.what.heading">What I edit</h2>'),
    ('<li><strong>Event films.</strong> Raw coverage shaped into a highlight film or a set of longer cuts.</li>',
     '<li><strong data-copy="editing.what.1.title">Event films.</strong> <span data-copy="editing.what.1.body">Raw coverage shaped into a highlight film or a set of longer cuts.</span></li>'),
    ('<li><strong>Performance and dance films.</strong> Work made for the screen, or a live show cut so it is worth watching.</li>',
     '<li><strong data-copy="editing.what.2.title">Performance and dance films.</strong> <span data-copy="editing.what.2.body">Work made for the screen, or a live show cut so it is worth watching.</span></li>'),
    ('<li><strong>Teasers and trailers.</strong> Short, sharp pieces to announce a show or an event.</li>',
     '<li><strong data-copy="editing.what.3.title">Teasers and trailers.</strong> <span data-copy="editing.what.3.body">Short, sharp pieces to announce a show or an event.</span></li>'),
    ('<li><strong>Showreels.</strong> A reel for a performer, a company, or a videographer.</li>',
     '<li><strong data-copy="editing.what.4.title">Showreels.</strong> <span data-copy="editing.what.4.body">A reel for a performer, a company, or a videographer.</span></li>'),
    ('<h2>How it works</h2>', '<h2 data-copy="editing.how.heading">How it works</h2>'),
    ('<p><em>Send the footage.</em> A link to a shared folder is enough. Tell me what the film is for, how long it should run, and where it will be seen.</p>',
     '<p><em data-copy="editing.how.1.title">Send the footage.</em> <span data-copy="editing.how.1.body">A link to a shared folder is enough. Tell me what the film is for, how long it should run, and where it will be seen.</span></p>'),
    ('<p><em>We agree the rounds.</em> Before I start, we settle how many rounds of feedback are included, so there are no surprises.</p>',
     '<p><em data-copy="editing.how.2.title">We agree the rounds.</em> <span data-copy="editing.how.2.body">Before I start, we settle how many rounds of feedback are included, so there are no surprises.</span></p>'),
    ('<p><em>I send a first cut.</em> You tell me what works and what does not, and I refine it.</p>',
     '<p><em data-copy="editing.how.3.title">I send a first cut.</em> <span data-copy="editing.how.3.body">You tell me what works and what does not, and I refine it.</span></p>'),
    ('<p><em>Then I finish it.</em> Sound, color, titles, and the files you need for every place the film will live.</p>',
     '<p><em data-copy="editing.how.4.title">Then I finish it.</em> <span data-copy="editing.how.4.body">Sound, color, titles, and the files you need for every place the film will live.</span></p>'),
    ('<h2>Music and rights</h2>\n    <p>Music has to be licensed for the way the film will be used. If you already have music, tell me where it comes from. If you do not, I can work with licensed tracks.</p>',
     '<h2 data-copy="editing.music.heading">Music and rights</h2>\n    <p data-copy="editing.music.body">Music has to be licensed for the way the film will be used. If you already have music, tell me where it comes from. If you do not, I can work with licensed tracks.</p>'),
    ('<h2>Remote or in person</h2>\n    <p>Most editing happens remotely, with footage arriving by link. If you are in Portland and would rather review a cut together, we can meet.</p>',
     '<h2 data-copy="editing.remote.heading">Remote or in person</h2>\n    <p data-copy="editing.remote.body">Most editing happens remotely, with footage arriving by link. If you are in Portland and would rather review a cut together, we can meet.</p>'),
    ('<h2>Questions</h2>\n    <h3>What footage can you work with?</h3>\n    <p>Most professional and consumer cameras. Tell me what you shot on and roughly how much there is.</p>\n    <h3>How long does it take?</h3>\n    <p>It depends on the length and complexity of the film. Tell me your deadline when you write, and I will say plainly whether it works.</p>\n    <h3>What does it cost?</h3>\n    <p>I quote by the project, once I know how much footage there is and what you want to end up with.</p>',
     '<h2 data-copy="editing.faq.heading">Questions</h2>\n    <h3 data-copy="editing.faq.1.q">What footage can you work with?</h3>\n    <p data-copy="editing.faq.1.a">Most professional and consumer cameras. Tell me what you shot on and roughly how much there is.</p>\n    <h3 data-copy="editing.faq.2.q">How long does it take?</h3>\n    <p data-copy="editing.faq.2.a">It depends on the length and complexity of the film. Tell me your deadline when you write, and I will say plainly whether it works.</p>\n    <h3 data-copy="editing.faq.3.q">What does it cost?</h3>\n    <p data-copy="editing.faq.3.a">I quote by the project, once I know how much footage there is and what you want to end up with.</p>'),
]

for old, new in ve_replacements:
    ve = replace_exact(ve, old, new)
if '<script src="/copy-editor.js" defer></script>' not in ve:
    ve = replace_exact(ve, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')
with open(ve_path, "w", encoding="utf-8") as f:
    f.write(ve)

# 5. Instrument now.html
now_path = os.path.join(ROOT, "now.html")
with open(now_path, "r", encoding="utf-8") as f:
    nw = f.read()

now_replacements = [
    ('<span>Devin Tucker</span></a>', '<span data-copy="global.brand_name">Devin Tucker</span></a>'),
    ('<h1>Now</h1>', '<h1 data-copy="now.heading">Now</h1>'),
    ('<p class="updated">Last updated <time datetime="2026-10-22">October 22, 2026</time>. A page for what I am up to at the moment, kept current.</p>',
     '<p class="updated"><span data-copy="now.updated_prefix">Last updated</span> <time datetime="2026-10-22" data-copy="now.updated_date">October 22, 2026</time>. <span data-copy="now.updated_note">A page for what I am up to at the moment, kept current.</span></p>'),
    ('<section class="item"><h2>Filming</h2><p>Event videography around Portland, and the occasional studio session with dancers, jugglers, and circus artists.</p></section>',
     '<section class="item"><h2 data-copy="now.1.title">Filming</h2><p data-copy="now.1.body">Event videography around Portland, and the occasional studio session with dancers, jugglers, and circus artists.</p></section>'),
    ('<section class="item"><h2>Editing</h2><p>Highlight films from this season\'s events, and a new cut of the showreel.</p></section>',
     '<section class="item"><h2 data-copy="now.2.title">Editing</h2><p data-copy="now.2.body">Highlight films from this season\'s events, and a new cut of the showreel.</p></section>'),
    ('<section class="item"><h2>Making</h2><p>A short film in collaboration with a performer. More soon.</p></section>',
     '<section class="item"><h2 data-copy="now.3.title">Making</h2><p data-copy="now.3.body">A short film in collaboration with a performer. More soon.</p></section>'),
    ('<section class="item"><h2>Booking</h2><p>Taking projects for spring 2027. The easiest way to reach me is the form on the main page.</p></section>',
     '<section class="item"><h2 data-copy="now.4.title">Booking</h2><p data-copy="now.4.body">Taking projects for spring 2027. The easiest way to reach me is the form on the main page.</p></section>'),
    ('<p class="back"><a class="textlink" href="index.html#contact">Tell me about your project</a></p>',
     '<p class="back"><a class="textlink" href="index.html#contact" data-copy="now.cta">Tell me about your project</a></p>'),
]
for old, new in now_replacements:
    nw = replace_exact(nw, old, new)
if '<script src="/copy-editor.js" defer></script>' not in nw:
    nw = replace_exact(nw, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')
with open(now_path, "w", encoding="utf-8") as f:
    f.write(nw)

# 6. Instrument hi.html
hi_path = os.path.join(ROOT, "hi.html")
with open(hi_path, "r", encoding="utf-8") as f:
    hi = f.read()

hi_replacements = [
    ('<span>Devin Tucker</span></a>', '<span data-copy="global.brand_name">Devin Tucker</span></a>'),
    ('<h1>Hello, I\'m Devin.</h1>\n  <p class="line">Live events and live art, on film.</p>',
     '<h1 data-copy="hi.heading">Hello, I\'m Devin.</h1>\n  <p class="line" data-copy="hi.tagline">Live events and live art, on film.</p>'),
    ('<a class="btn" href="devin-tucker.vcf" download>Save my contact</a>\n    <a class="btn ghost" href="index.html#top">Watch the reel</a>\n    <a class="btn ghost" href="mailto:hello@yourdomain.com">Write to me</a>\n    <a class="btn ghost" href="https://cal.com/yourname/intro" target="_blank" rel="noopener">Book a short call</a>',
     '<a class="btn" href="devin-tucker.vcf" download data-copy="hi.btn_save">Save my contact</a>\n    <a class="btn ghost" href="index.html#top" data-copy="hi.btn_reel">Watch the reel</a>\n    <a class="btn ghost" data-email-href href="mailto:hello@yourdomain.com" data-copy="hi.btn_email">Write to me</a>\n    <a class="btn ghost" data-book href="https://cal.com/yourname/intro" target="_blank" rel="noopener" data-copy="hi.btn_book">Book a short call</a>'),
    ('<p class="more"><a class="textlink" href="index.html">See the full site</a></p>',
     '<p class="more"><a class="textlink" href="index.html" data-copy="hi.full_site">See the full site</a></p>'),
    ('<figcaption>Scan to open this card on another phone.</figcaption>',
     '<figcaption data-copy="hi.qr_cap">Scan to open this card on another phone.</figcaption>'),
]
for old, new in hi_replacements:
    hi = replace_exact(hi, old, new)
if '<script src="/copy-editor.js" defer></script>' not in hi:
    hi = replace_exact(hi, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')
with open(hi_path, "w", encoding="utf-8") as f:
    f.write(hi)

# 7. Instrument 404.html
f404_path = os.path.join(ROOT, "404.html")
with open(f404_path, "r", encoding="utf-8") as f:
    f404 = f.read()

f404_replacements = [
    ('<span>Devin Tucker</span></a>', '<span data-copy="global.brand_name">Devin Tucker</span></a>'),
    ('<h1>That page isn\'t here.</h1>\n  <p class="lede">The rings are keeping busy, though. While they do, here are a few places that do exist.</p>',
     '<h1 data-copy="notfound.heading">That page isn\'t here.</h1>\n  <p class="lede" data-copy="notfound.lede">The rings are keeping busy, though. While they do, here are a few places that do exist.</p>'),
    ('<a class="btn" href="index.html">Back to the start</a>\n    <a class="textlink" href="index.html#work">See the work</a>\n    <a class="textlink" href="index.html#contact">Say hello</a>',
     '<a class="btn" href="index.html" data-copy="notfound.btn_home">Back to the start</a>\n    <a class="textlink" href="index.html#work" data-copy="notfound.link_work">See the work</a>\n    <a class="textlink" href="index.html#contact" data-copy="notfound.link_contact">Say hello</a>'),
]
for old, new in f404_replacements:
    f404 = replace_exact(f404, old, new)
if '<script src="/copy-editor.js" defer></script>' not in f404:
    f404 = replace_exact(f404, '</body>', '<script src="/copy-editor.js" defer></script>\n</body>')
with open(f404_path, "w", encoding="utf-8") as f:
    f.write(f404)

# Extract all data-copy keys and initial values into content.json
copy_values = {}
pages = [
    "index.html",
    "event-videography-portland/index.html",
    "dance-and-performance-film-portland/index.html",
    "video-editing-portland/index.html",
    "now.html",
    "hi.html",
    "404.html",
]
pattern = re.compile(r'data-copy="([^"]+)">([^<]*)</')
for rel in pages:
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
        text = f.read()
    for m in pattern.finditer(text):
        key, val = m.group(1), m.group(2)
        copy_values[key] = val

data = {
    "settings": {
        "email": copy_values.get("global.email", "hello@yourdomain.com"),
        "bookingUrl": "https://cal.com/yourname/intro",
        "formEndpoint": "",
        "domain": "https://www.yourdomain.com"
    },
    "copy": copy_values
}

with open(os.path.join(ROOT, "content.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Successfully instrumented all pages and saved {len(copy_values)} copy keys to content.json!")
