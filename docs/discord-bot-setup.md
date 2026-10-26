# Discord Bot Setup

This guide walks you through:

- creating the bot,
- turning on Message Content Intent,
- getting the bot token,
- inviting the bot to your server with the right permissions.

Do [discord-server-setup.md](discord-server-setup.md) first. You need your own server before you can invite the bot.

You will work in a web browser, such as Safari or Chrome, on your Mac.

---

> ## ⚠️ The bot token is a password
>
> The **bot token** is the password the agent uses to log in as your bot. Anyone who has it can control your bot: read your channel, post messages, and act as the bot in your server.
>
> - **Never share it** with anyone, including your partner or classmates.
> - **Never paste it into this chat** with Claude, or any other AI chat, website or screenshot.
> - **Never commit it.** It goes only in the `.env` file, which Git ignores. It must never appear in code, `README.md`, or any file in `docs/`.
>
> If it ever leaks, go straight to Part 3 and click **Reset Token**. The old token stops working immediately.

---

## Part 1 – Create the application and bot

*Application*: your project's entry in Discord's Developer Portal. Each application comes with one *bot*, a special Discord account that programs control.

1. In your browser, go to **https://discord.com/developers/applications**.
2. Log in with the **same Discord account** that owns your server.
3. At the top right, click **New Application**.
4. In **Name**, type `Produce Freshness Agent`.
5. Tick the box agreeing to Discord's Developer Terms of Service and Developer Policy.
6. Click **Create**.
7. (If asked) complete the "I am human" check.

You are now on your application's **General Information** page.

8. (Optional) Under **App Icon**, upload a picture, for example a fruit emoji image. This becomes the bot's profile picture.
9. If you changed anything, click **Save Changes** in the green bar at the bottom.

---

## Part 2 – Turn on Message Content Intent

*Intent*: a switch that tells Discord which kinds of information your bot is allowed to receive. **Message Content** is a *privileged intent*, so Discord keeps it off until you turn it on yourself.

**Why it's needed:** without Message Content Intent, Discord hides a message's text **and its attachments** from the bot. The agent would see that someone posted something, but it would never receive the photo, so it couldn't do anything.

1. In the left menu, click **Bot**.
2. Scroll down to the section **Privileged Gateway Intents**.
3. Turn on **Message Content Intent**.
4. Leave **Presence Intent** and **Server Members Intent** **off**, because the agent doesn't need them.
5. Click **Save Changes** in the green bar at the bottom.

---

## Part 3 – Get the bot token

You will see the token **only once**. Have your `.env` file ready before you click (see "Put the token in `.env`" below).

1. Stay on the **Bot** page in the left menu.
2. Near the top, under **Token**, click **Reset Token**.
3. Click **Yes, do it!** to confirm.
4. If asked, enter your Discord password or two-factor code, then click **Submit**.
5. Click **Copy** under the new token. Don't screenshot it, and don't paste it anywhere except `.env`.

If you lose the token, you can't view it again. Just repeat this part to get a new one, and replace the old one in `.env`.

### Put the token in `.env`

*`.env` file*: a private settings file in the project folder that the agent reads on start-up. Git ignores it, so it is never committed.

1. Open the project folder `Produce-Photo-Agent` in your code editor, such as VS Code.
2. If there is no file named `.env` yet, create a new file with exactly that name, including the dot at the start, in the project folder (next to `README.md`).
3. Add this line, pasting your token after the `=` with no spaces and no quotes:
   ```
   DISCORD_TOKEN=paste-your-token-here
   ```
4. Add your channel ID from the server guide on the next line:
   ```
   CHANNEL_ID=123456789012345678
   ```
5. Save the file (**⌘ Command + S**).

The other two settings, `CLAUDE_MODEL` and `DATA_DIR`, will be explained when the code is written.

> **Finder tip:** macOS hides files whose names start with a dot. To see `.env` in Finder, press **⌘ Command + Shift + .** (period). Press it again to hide them.

---

## Part 4 – Make the bot private (recommended)

This stops other people from adding your bot to *their* servers, where they would be using your Claude usage.

1. In the left menu, click **Installation**.
2. Under **Install Link**, choose **None**.
3. Click **Save Changes**.
4. In the left menu, click **Bot**.
5. Turn **Public Bot** **off**.
6. Click **Save Changes**.

> If Discord shows the error *"Private application cannot have a default authorization link"*, you skipped steps 1–3. Do them first, then try step 5 again.

---

## Part 5 – Invite the bot to your server

You will build an *invite link* (Discord calls it an *OAuth2 URL*) that adds the bot to your server with exactly the permissions it needs.

**The four permissions and why:**

| Permission | Why the agent needs it |
|---|---|
| **View Channels** | To see `#produce-check` and its messages |
| **Send Messages** | To post its replies |
| **Read Message History** | To reply *to* a specific message (Discord requires this for replies) |
| **Add Reactions** | To add the ⏳ reaction while it's working |

Don't tick anything else. In particular, never tick **Administrator**.

1. In the left menu, click **OAuth2**.
2. Scroll down to **OAuth2 URL Generator**.
3. Under **Scopes**, tick **bot**. A **Bot Permissions** box appears below.
4. Under **Bot Permissions**, in the **Text Permissions** column, tick **Send Messages**.
5. Tick **Read Message History**.
6. Tick **Add Reactions**.
7. In the **General Permissions** column, tick **View Channels**.
8. Check that exactly these four permissions are ticked.
9. If there is an **Integration Type** option, choose **Guild Install**.
10. At the bottom, next to **Generated URL**, click **Copy**.
11. Paste the link into your browser's address bar and press **Return**.
12. Under **Add to Server**, choose your server, e.g. **Produce Lab**. Only servers you own or manage appear here.
13. Click **Continue**.
14. Check that the four permissions are listed and ticked.
15. Click **Authorize**.
16. Complete the "I am human" check if asked.
17. Go back to the Discord app. The bot now appears in your server's member list, shown as **offline**. This is expected: it comes online only when the agent program is running.

The invite link isn't a secret like the token, but there's no need to share it. With **Public Bot** off, only you can use it anyway.

---

## Part 6 – Only if `#produce-check` is a private channel

Skip this part if you left **Private Channel** off when creating the channel.

1. In the Discord app, hover over `#produce-check` and click its **gear icon** (**Edit Channel**).
2. In the left menu, click **Permissions**.
3. Click **Add members or roles**.
4. Type the bot's name, `Produce Freshness Agent`, and tick it.
5. Click **Done**.
6. Make sure the bot has **View Channel**, **Send Messages**, **Read Message History** and **Add Reactions** set to the green tick ✓.
7. Click **Save Changes** if a bar appears at the bottom.
8. Also add your partner the same way, so they can see the channel and post in it.

---

## What you should have now

- [ ] An application and bot called **Produce Freshness Agent**
- [ ] **Message Content Intent** turned on
- [ ] The **bot token** saved **only** in `.env` as `DISCORD_TOKEN=…`
- [ ] `CHANNEL_ID=…` in `.env`
- [ ] **Public Bot** off
- [ ] The bot is a member of your server (offline for now) and can see `#produce-check`

**Final check:** in the terminal in the project folder, run `git status`. `.env` must **not** appear in the list. If it does, stop and don't commit. Something is wrong with `.gitignore`.
