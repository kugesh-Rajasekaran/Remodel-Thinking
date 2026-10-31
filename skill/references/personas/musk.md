---
id: musk
name: Elon Musk
essence: Question every requirement, price from the atoms up, iterate fast
best_for: When a product feels slow or costly and you accept its requirements and costs as given
watch_out: Turning internal stretch deadlines into public promises (FSD, robotaxi, "funding secured")
---

# Elon Musk: Question every requirement, price from the atoms up, iterate fast

## In one minute
- Built or led Zip2 (sold to Compaq for $307M, 1999), X.com/PayPal (sold to eBay for $1.5B in stock, 2002), SpaceX, Tesla, Starlink, Neuralink, The Boring Company, and bought Twitter/X for $44B in 2022 [19][20].
- His core habit is a strict order of operations he calls "the algorithm": make requirements less dumb, delete, simplify, speed up, automate. He says he learned the order by getting it wrong [1][2].
- He sets costs and deadlines from physics and raw inputs, not from what the market charges or what teams estimate. That gave him reusable rockets and Starlink, and also a decade of missed self-driving dates [12][23][26].
- He tests real hardware until it breaks and treats the failure as data. Three Falcon 1 failures nearly ended SpaceX in 2008 [4][5].

## Mental models (what they believe)

### Make the requirement less dumb, then delete the part, and only then optimise
- **Belief:** Most waste sits in parts and steps that should not exist. Optimising them first makes the waste permanent. "possibly the most common error of a smart engineer is to optimize the thing that should not exist" [1].
- **Real decision:** On the Model 3 line (2017-18) Tesla automated first. Musk scrapped a "crazy complex network of conveyor belts" and tweeted "excessive automation at Tesla was a mistake. To be precise, my mistake" [6]. By 2021 he taught the five steps in order and said "I have personally made the mistake of going backwards on all five steps multiple times" [1].
- **Ask yourself:** Who, by name, set this requirement, and what happens if I delete it?
- **In a founder's prompts:** With it: "Who asked for per-seat usage reports? If only one customer, cut it from v1 and show me what else in billing nobody uses." Without it: "Optimise the usage report flow and add caching so it is faster."

### Every requirement needs a named owner, and smart people's requirements are the riskiest
- **Belief:** A requirement from "legal" or "the customer" is not a requirement. Each one traces to a person who can be questioned. "it's particularly dangerous if a smart person gave you the requirements because you might not question them enough" [1].
- **Real decision:** Musk's rule of thumb is to delete so hard that you end up adding back at least 10% of what you cut. If you never add anything back, you did not delete enough [1][2].
- **Ask yourself:** If no one will put their name on this requirement, why am I building it?
- **In a founder's prompts:** With it: "List every rule in the invoice module and which law or customer each one comes from." Without it: "Make sure the invoice module supports all the usual edge cases."

### Price it from the atoms up, then build in-house only where the markup is absurd
- **Belief:** A product's floor cost is its raw inputs. The gap between that floor and the market price shows how much waste there is to remove. Isaacson calls his ratio of total cost to raw-material cost the "idiot index" [29].
- **Real decision:** In 2002 Russian sellers offered him one refurbished ICBM for $8M. He turned it down and founded SpaceX [20]. Unhappy with what US suppliers charged, SpaceX built the Merlin engine, flight computers and rocket body itself [22]. At Tesla he found each Roadster cost $140k in parts while selling for $92k, a "life threatening problem". Almost every major system was then redesigned, retooled or moved to a new supplier [21].
- **Ask yourself:** What does one customer account cost me per month from the inputs up, and which line is many times its floor?
- **In a founder's prompts:** With it: "Break our per-account monthly cost into cloud, SMS, payment fees and support minutes, and rank them." Without it: "Competitor X charges $49, so set our plan at $45."

### Make the expensive thing reusable, and find the business that pays for it
- **Belief:** Throwing away hardware is the main cost, so reuse is the lever. "If one can figure out how to effectively reuse rockets just like airplanes, the cost of access to space will be reduced by as much as a factor of 100" [23]. The order matters too: an expensive first product funds the cheaper one. His 2006 plan was a sports car, then an affordable car, then an even cheaper one [3].
- **Real decision:** After two failed drone-ship landing attempts in 2015, a Falcon 9 first stage landed at Landing Zone 1 on 21 Dec 2015 [24]. Starlink then grew from 2.3M subscribers (2023) to 8.9M (2025). Connectivity brought in $11.4B, 61% of SpaceX's $18.7B 2025 revenue, while about $3B went to Starship R&D [26].
- **Ask yourself:** What do I rebuild or redo for every customer that I could build once and reuse?
- **In a founder's prompts:** With it: "Onboarding each account takes 2 days of manual data entry. Design a reusable import so account #50 costs nothing." Without it: "Write a script to speed up data entry for this new account."

### Test real hardware until it fails, because failure is the data
- **Belief:** Flying development hardware teaches faster than analysis. SpaceX: "Testing development flight hardware in a flight environment is what enables our teams to quickly learn" [25].
- **Real decision:** Falcon 1 failed three times before reaching orbit in September 2008. Musk: "Having four strikes is really kaput" [4][5]. Starship's first integrated flight (20 Apr 2023) was destroyed in under four minutes and wrecked a pad built with no flame trench. The FAA closed its review with 63 corrective actions [25].
- **Ask yourself:** What is the cheapest real-world test this week that could prove me wrong?
- **In a founder's prompts:** With it: "Ship the export fix behind a flag to one customer tonight and log every failure." Without it: "Add more unit tests and mocks before we let anyone use it."

### The factory is the product
- **Belief:** "Making the machine that makes the machine is vastly harder than the machine itself" [11].
- **Real decision:** At Battery Day 2020 he targeted a 56% cut in cost per kWh through cell design, the manufacturing process (dry electrode), materials and vehicle integration, all made in-house [11]. He admitted the dry electrode was "close to working, but not with a good yield" [11].
- **Ask yourself:** Am I improving the product, or the system that produces and ships it every week?
- **In a founder's prompts:** With it: "What in our release and onboarding pipeline limits us to 3 new accounts a week?" Without it: "Add a new report screen."

## Thinking process (the order of their steps)
1. **Anchor on the physics limit, not the industry norm.** Example: reuse could cut the cost of reaching space by up to 100x [23].
2. **Question each requirement and name its owner.** Example: smart people's requirements get the hardest look [1].
3. **Delete parts and process steps.** If you add back less than 10% of what you cut, you did not cut enough [1][2].
4. **Simplify and optimise only what survived.** Example: never optimise a thing that should not exist [1].
5. **Accelerate cycle time with an aggressive deadline.** "don't go faster until you've worked on the other three things first" [2]. Example: after the third Falcon 1 failure, SpaceX flew the next rocket to Kwajalein by military plane instead of ship. It buckled in flight, the repair took two weeks instead of the expected three months, and it launched in late September 2008 [5].
6. **Test in the real environment and fix fast.** Example: the loss of Starship flight 1 became 63 corrective actions, including a pad redesign [25].
7. **Automate last.** Example: the Model 3 conveyor system was scrapped and the five-step order was set with automation at the end [1][6].

## More done at the same quality
- **Leave meetings that do not need you.** "Walk out of a meeting or drop off a call as soon as it is obvious you aren't adding value. It is not rude to leave, it is rude to make someone stay and waste their time." He also told staff to cut large and frequent meetings (Tesla email, April 2018) [8].
- **Use the shortest communication path.** "Communication should travel via the shortest path necessary to get the job done, not through the 'chain of command'." He also banned acronyms and made-up words [8].
- **Change rules that are obviously wrong.** If following a company rule is obviously ridiculous in a situation, "then the rule should change" [8].
- **Work where the constraint is.** During Model 3 "production hell" he slept at the Fremont factory: "I don't have time to go home and shower" [7].
- **Correct publicly and fast.** He tweeted that the automation error was his own on the day the CBS interview aired, in which he said the conveyor system had already been ripped out [6].

## Wins that came from the thinking
| Decision | Year | Thinking used | Outcome |
|---|---|---|---|
| Turn down an $8M Russian rocket and build one | 2002 | Price from the atoms up | Falcon 1 reached orbit on its 4th try (Sept 2008); NASA contract came Christmas week 2008 [4][5][20] |
| Fly Falcon 1 to Kwajalein instead of shipping it | 2008 | Aggressive deadline | Repair took 2 weeks instead of 3 months; launched late Sept 2008 [5] |
| Land and reuse the booster | 2015 | Reuse the expensive thing | First orbital-class booster landing, 21 Dec 2015, after two failed attempts [24] |
| Roadster first, cheaper cars later | 2006 | Expensive product funds the cheap one | Plan published 2 Aug 2006 and followed in that order [3] |
| Starlink as SpaceX's cash engine | 2019-25 | Vertical integration plus sequencing | 8.9M subscribers and 61% of revenue in 2025; funds about $3B/yr of Starship R&D [26] |

## Failures and what they show
| Failure | Year | What went wrong in the thinking | What changed after |
|---|---|---|---|
| Kept from the CEO role at Zip2; replaced as X.com CEO by Thiel | 1999-2000 | Pushed his own direction (e.g. Microsoft over Unix software) without the board and team behind him [20] | Kept control later: majority holder and chairman of Tesla from 2004; founded SpaceX with $100M of his own money as CEO [20] |
| Model 3 over-automation | 2017-18 | Automated before deleting and simplifying, and put too much new tech in at once. Target was 2,500/week by end of Q1 2018; actual was 2,020 [6] | Conveyors scrapped, "my mistake" tweet; later taught automation as the last step [1][6] |
| "Funding secured" tweet ($420/share) | 2018 | Announced a deal as near-certain before discussing terms or price with financing partners [9] | SEC settlement: $20M each from Musk and Tesla, stepped down as chairman, controls on his communications. A 2023 jury found him not liable to investors [9][10] |
| Self-driving and robotaxi dates | 2016-25 | Treated stretch timelines and a 2016 "hardware required" claim as customer promises; a 2022 small-claims judge called that claim "false advertising" [12] | Jan 2025: said HW3 FSD buyers' computers must be upgraded. Robotaxi launched in Austin in June 2025 with a safety monitor on board [12][14] |
| Twitter/X cuts | 2022-23 | Deleted at company scale: about half of staff laid off within days of closing, then an ultimatum to be "extremely hardcore" [15] | He cited a ~50% drop in ad revenue plus heavy debt as the reason for negative cash flow (July 2023) and called the firings "not fun at all" [16][17] |

## Public image vs how they actually decide
- **Image:** a visionary of grand missions. **Reality:** much of his time goes to part-level and requirement-level detail on the factory floor, as the Starbase tour shows [1][2].
- **Image:** a reckless gambler. **Reality:** the risk is deliberate test-to-failure with hardware he can afford to lose. When the margin ran out (2008), both companies nearly died [4].
- **Image:** deadlines are hype. **Reality:** internally they force first-principles redesign [5]. Externally they become liabilities: "Punctuality is not my strong suit, but I always come through in the end" [13]. Neuralink human trials were called imminent from 2019, and the FDA rejected the 2022 application on safety grounds [27]. The Chicago O'Hare tunnel won in 2018 and was reported likely dead by 2019 [28].
- **Image:** never admits error. **Reality:** he reverses in public when the data is clear: automation (2018) and HW3 (2025) [6][12].

## Don't copy
- **Public dates built from internal stretch goals.** For a small software company, a missed go-live date costs a customer a launch and costs you the account [12][13].
- **Market-moving or customer-facing claims without a documented basis.** "Funding secured" cost $40M in penalties and his chairmanship [9]. In 2024 a Delaware court rescinded his pay package over a flawed board process; the remedy was reversed in December 2025 [30][31].
- **Deleting people at Twitter scale.** In a small team each person holds customer relationships. Cutting at that scale while revenue is also falling is a double hit [15][16].

## Applied to a founder
- Musk would make you name the customer or person behind every feature request before the agent writes a line, and delete any feature that has no name.
- Musk would build a per-account cost tree (cloud, SMS, payment fees, support minutes, onboarding hours) and attack the biggest line, not the cleanest code.
- Musk would put this week's build in front of one real customer behind a flag and treat the crash log as the spec.
- Musk would turn customer onboarding into a "machine that builds the machine": a reusable import and config so account #100 costs close to zero.
- Musk would use a high-margin product (e.g. an enterprise tier) to fund a cheap, mass-market plan, as the 2006 plan did [3].
- Musk would delete and merge manual steps before asking the agent to automate any workflow.

## Bottleneck checks
| Bottleneck in your thinking | You see it when your prompts... | Musk's fix (one question) |
|---|---|---|
| Optimising before deleting | ask to "refactor", "speed up", "optimise" or "add caching" for a feature, but never ask whether it should exist | Should this part exist at all? |
| Unowned requirements | say "we need to support X" or "it must handle Y" without naming the customer, user or law behind it | Who, by name, asked for this? |
| Pricing by analogy | set price or vendor choice by what a competitor charges; never ask for cost per account or order | What does this cost from the inputs up? |
| Automating too early | ask for scripts, cron jobs, CI or agents for a process that has run manually only a few times | Which steps can I delete before automating the rest? |
| Comfortable timelines | give no deadline, say "when you can", or plan in weeks what could ship in days | What would it take to ship this in a tenth of the time? |
| Testing only in staging | ask for more mocks and unit tests but never ask to ship to a real customer behind a flag | What is the fastest real-world test that could prove me wrong? |
| Builder-only scope | keep every prompt about code; never ask about unit economics, onboarding cost, sales or cash | What is the company's limiting factor right now? |
| Rebuilding per customer | ask for one-off fixes, configs or scripts "for this customer" | What do I build once so the next customer costs nothing? |

## Voice
How Remodel writes a report in this persona's lens. The steps are the order every problem is
walked through; only lines in this file's sources may appear in quotation marks.
- **Tone:** Blunt engineer. Names the waste in one line, then the fix. Short sentences, no comfort.
- **Steps:** Question the requirement | Delete | Simplify | Accelerate | Automate
- **Deadlines:** Days, set at the physics limit. Never "this week" or "soon".
- **Lands like:** This step should not exist. Delete it, then build the import once.

## Practice cards

```yaml
id: musk-name-the-requirement
type: model
title: Name who asked, then try to delete it
old: Treat a feature or rule as given and ask the agent to build or optimise it
when: you ask the agent to optimise, refactor, speed up or add support for something
question: Who, by name, required this, and could the part be deleted instead?
trigger: '(?i)\b(optimi[sz]e|refactor|speed up|make (it|this) faster|add support for|must support|need to support)\b'
proof: '(?i)\b(who (asked|needs|wants)|which (customer|client|account|user)|delete|remove|drop|do we (even )?need|should (this|it) exist)\b'
agent_line: Before optimising, state in one line who requires this and whether deleting it is an option, then proceed.
caution_after: 3
```

```yaml
id: musk-cost-from-inputs
type: model
title: Price it from the inputs up
old: Set a price or pick a vendor by looking at competitors or vendor quotes
when: you ask about pricing, plans, vendor choice or cost
question: What is the floor cost per account from raw inputs, and how many times above it are we paying or charging?
trigger: '(?i)\b(pricing|price (plan|point)|subscription plan|per (account|seat|user)|vendor|quote|competitor|cheaper (option|alternative))\b'
proof: '(?i)\b(unit cost|cost per (account|order|customer|client|user)|floor cost|input costs?|cost breakdown|cost tree|gross margin)\b'
agent_line: When pricing or choosing a vendor, first list per-account input costs and the ratio of price to those inputs.
caution_after: 3
```

```yaml
id: musk-automate-last
type: process
title: Delete and simplify steps before automating them
old: Ask the agent to script, schedule or automate a manual workflow straight away
when: you ask the agent to automate, script, schedule or add CI or cron for a process
question: Which steps of this process can I delete or merge before automating what is left?
trigger: '(?i)\b(automate|automation|cron( job)?|schedule (a|the) job|write a script to|pipeline for)\b'
proof: '(?i)\b(delete (the |a )?steps?|remove (the |a )?steps?|skip (the |a )?steps?|fewer steps|merge (the )?steps|simplify (the )?(flow|process|steps))\b'
agent_line: Before automating, list the current steps and mark which can be deleted or merged; automate only the rest.
caution_after: 3
```

## Sources
[1] Starbase Tour with Elon Musk, Part 1 (caption transcript), Everyday Astronaut / Tim Dodd, 2021, https://rosetta.to/u/everydayastronaut/starbase-tour-with-elon-musk-part-1-summer-2021
[2] Starbase Tour and Interview with Elon Musk (cliff notes), Everyday Astronaut, 2021, https://everydayastronaut.com/starbase-tour-and-interview-with-elon-musk/
[3] The Secret Tesla Motors Master Plan (just between you and me), Elon Musk, Tesla blog, 2006, https://www.tesla.com/secret-master-plan
[4] Billionaire Elon Musk on 2008: "The worst year of my life", CBS News / 60 Minutes, 2014, https://www.cbsnews.com/news/billionaire-elon-musk-on-2008-the-worst-year-of-my-life
[5] Review of Ashlee Vance's Elon Musk (Falcon 1, Kwajalein), The Space Review, 2015, https://thespacereview.com/article/2751/1
[6] Musk on Model 3 robots, CBS interview and "Humans are underrated" tweet, Fortune, 2018, https://fortune.com/2018/04/13/tesla-elon-musk-robot-human-model-3
[7] Elon Musk Explains Why He's Still Sleeping on the Tesla Factory Floor, Entrepreneur, 2018, https://www.entrepreneur.com/article/311927
[8] Elon Musk's productivity rules, according to a Tesla email, CNBC, 2018, https://www.cnbc.com/2018/04/18/elon-musks-productivity-rules-according-to-tesla-email.html
[9] Press release 2018-226: Elon Musk Settles SEC Fraud Charges; Tesla Charged With and Resolves Securities Law Charge, U.S. SEC, 2018, https://www.sec.gov/news/press-release/2018-226
[10] Musk and Tesla found not liable in securities class action over 2018 tweets, CNBC, 2023, https://www.cnbc.com/2023/02/03/musk-not-liable-in-securities-class-action-suit.html
[11] Tesla Battery Day: 'tabless' 4680 cell and a $25k car, electrive, 2020, https://www.electrive.com/2020/09/23/tesla-battery-day-tabless-4680-cell-and-in-house-production
[12] Elon Musk reveals Elon Musk was wrong about Full Self-Driving, TechCrunch, 2025, https://techcrunch.com/2025/01/30/elon-musk-reveals-elon-musk-was-wrong-about-full-self-driving/
[13] Elon Musk admits he lacks punctuality but Tesla has still delivered, InsideEVs, 2020, https://insideevs.com/news/420688/elon-musk-admits-he-lacks-punctuality-but-tesla-has-still-delivered/
[14] Tesla launches robotaxi service in Austin with 20 Model Y, electrive, 2025, https://www.electrive.com/2025/06/23/tesla-launches-robotaxi-service-in-austin-with-20-model-y
[15] Elon Musk email: be part of hardcore Twitter or leave, Gizmodo, 2022, https://gizmodo.com/elon-musk-email-be-part-of-hardcore-twitter-or-leave-1849789128
[16] Elon Musk says Twitter still in 'negative cash flow' due to 50% drop in advertising, debt, KTVU FOX 2, 2023, https://www.ktvu.com/news/elon-musk-says-twitter-sees-drop-advertising-revenue
[17] In surprise BBC interview, Elon Musk says owning Twitter at times painful, SiliconANGLE, 2023, https://siliconangle.com/2023/04/12/surprise-interview-bbc-elon-musk-says-owning-twitter-times-painful/
[18] Twitter wins bid for expedited trial to force Musk to close $44 billion acquisition, NBC News, 2022, https://www.nbcnews.com/business/corporations/twitter-wins-bid-expedited-trial-force-musk-close-44-billion-acquisiti-rcna38935
[19] Musk Closes $44 Billion Twitter Deal, Fires Top Executives, Bloomberg Law, 2022, https://news.bloomberglaw.com/mergers-and-acquisitions/musk-completes-44-billion-twitter-deal-ending-months-of-enmity
[20] Business career of Elon Musk (citing Vance 2017, Isaacson 2023, PayPal 10-K), Wikipedia, accessed 2026, https://en.wikipedia.org/wiki/Business_career_of_Elon_Musk
[21] Musk broadside at Eberhard (quotes Musk's 2009 Tesla blog post), The Register, 2009, https://www.theregister.com/2009/06/23/musk_broadside_eberhard
[22] Why Is The U.S. Space Industry So Obsessed With Vertical Integration?, Garrett Reim, Aviation Week, 2024, https://aviationweek.com/space/commercial-space/why-us-space-industry-so-obsessed-vertical-integration-0
[23] SpaceX, NASA launching reusable rocket, Sharon Gaudin, Computerworld, 2014, https://www.computerworld.com/article/2488585/spacex--nasa-launching-reusable-rocket.html
[24] Falcon 9 flight 20, Wikipedia, accessed 2026, https://en.wikipedia.org/wiki/Falcon_9_flight_20
[25] FAA's Mishap Investigation Into Starship Launch Ends With 63 Action Items, Via Satellite, 2023, https://www.satellitetoday.com/launch/2023/09/08/faas-mishap-investigation-into-starship-launch-ends-with-63-action-items/
[26] SpaceX's IPO Filing Gives First Look Into Company's Financials, Via Satellite, 2026, https://www.satellitetoday.com/finance/2026/05/20/spacexs-ipo-filing-gives-first-look-into-companys-financials/
[27] Neuralink's request for human trials of brain implants was reportedly rejected by the FDA, Popular Science, 2023, https://www.popsci.com/technology/neuralink-fda-delay/
[28] Elon Musk O'Hare Express project is likely dead, Mass Transit, 2019, https://masstransitmag.com/alt-mobility/news/21070294/elon-musk-ohare-express-project-is-likely-dead-heres-where-lightfoot-and-preckwinkle-stand-on-transportation-issues
[29] Elon Musk, Walter Isaacson, Simon & Schuster, 2023 (book; used only for the "idiot index" term, corroborated by multiple summaries)
[30] How much can Tesla pay Elon Musk? Delaware's Supreme Court will decide, NPR, 2025, https://www.npr.org/2025/10/15/nx-s1-5567930/elon-musk-tesla-compensation-case-appeal
[31] Musk's $56 billion Tesla pay package must be restored, Delaware Supreme Court rules, CNBC, 2025, https://www.cnbc.com/2025/12/19/musk-tesla-pay-delaware-supreme-court.html
