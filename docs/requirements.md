# Produce Freshness Agent – Requirements

## What I want to build
A Discord agent: when someone posts a photo of a fruit or vegetable in a specific channel, it identifies the item, whether it's a fruit or vegetable, how ripe/fresh it is (0-100), whether it's ready to eat (Yes / Not yet / Past its best), roughly how many days it will stay good, and a short storage tip. It replies in the channel and logs everything to Excel.

## What users do
- Post a photo of a fruit or vegetable in the channel (optionally with a short message)
- Wait for the agent's reply

## What to record
- Time, uploader, fruit/vegetable, item name, freshness score, ready to eat, estimated days left, storage tip, confidence, photo location
- How many items were checked today (total, fruits, vegetables)

## What I already know
- Python, `claude -p` to look at photos, Discord Gateway (bot) mode
- Records saved to an Excel file that keeps growing (append, not overwrite)

## What I'm not sure about
- What to do when the photo isn't a fruit or vegetable
- What happens when many people post at once
