# Discord Server Setup

This guide walks you through:

- creating your own Discord server,
- creating a channel for the Produce Freshness Agent and finding its `CHANNEL_ID`,
- inviting your partner.

It assumes you use the **Discord desktop app on macOS**. The website (discord.com/app) looks almost the same.

> **Right-click on a Mac:** where a step says *right-click*, you can also hold **Control** and click, or click with two fingers on the trackpad.

---

## Part 1 – Create your own server

*Server*: your own private space on Discord, with its own channels and members.

1. Open the **Discord** app and log in.
2. In the narrow column of round icons on the far left, scroll to the bottom.
3. Click the green **+** icon (**Add a Server**).
4. Click **Create My Own**.
5. Click **For me and my friends**.
6. In **Server Name**, type a name, for example `Produce Lab`.
7. (Optional) Click the round camera icon to upload a server picture.
8. Click **Create**.

Your new server opens, and its icon now appears in the left column.

---

## Part 2 – Create the agent's channel

*Channel*: a chat room inside a server. The agent will listen to exactly one channel.

### 2a. Create the channel

1. In the channel list (the second column from the left), find the heading **TEXT CHANNELS**.
2. Hover over **TEXT CHANNELS** and click the small **+** that appears to its right (**Create Channel**).
3. Under **Channel Type**, choose **Text**.
4. In **Channel Name**, type `produce-check`.
5. Leave **Private Channel** **off**, so you, your partner and the bot can all see it. (If you turn it on, you will have to add the bot to the channel by hand, as described in the bot guide, Part 6.)
6. Click **Create Channel**.

`#produce-check` now appears under TEXT CHANNELS.

### 2b. Turn on Developer Mode

Developer Mode adds a **Copy ID** option to Discord's menus. You need it to copy the channel's ID.

1. At the bottom-left of the Discord window, next to your name, click the **gear icon** (**User Settings**).
2. In the left menu, scroll down to the **App Settings** section.
3. Click **Advanced**.
4. Turn on the **Developer Mode** switch, so it turns blue or green.
5. Press **Esc** (or click the **X** at the top right) to close settings.

### 2c. Copy the CHANNEL_ID

*Channel ID*: a long number, such as `123456789012345678`, that identifies one channel. The agent uses it to know which channel to watch.

1. In the channel list, **right-click** `#produce-check`.
2. At the bottom of the menu, click **Copy Channel ID**.
3. Paste it somewhere safe for now (press **⌘ Command + V**), for example in a Notes note.

You will put it in the `.env` file as `CHANNEL_ID=…` later. Unlike the bot token, the channel ID is **not a secret**.

> **Check:** the copied value should be only digits, usually 17–20 of them. If you see letters or a `https://` link, you clicked **Copy Link** instead. Repeat step 2.

---

## Part 3 – Invite your partner

*Invite link*: a link that lets someone join your server.

1. In the top-left corner of the channel list, click your **server name**. A menu opens.
2. Click **Invite People**.
3. In the window that opens, click **Edit invite link** at the bottom.
4. Set **Expire After** to **1 day** (or **7 days** if your partner might join later).
5. Set **Max Number of Uses** to **1 use**, so only one person can use this link.
6. Click **Generate a New Link**.
7. Click **Copy** next to the link.
8. Send the link to your partner **privately**, for example in a direct message. Don't post it anywhere public.
9. When your partner opens the link and clicks **Accept Invite**, they will appear in your server's member list.

> **Tip:** if the link expires or gets used up before your partner joins, just repeat Part 3 to make a new one.

---

## What you should have now

- [ ] Your own server, e.g. **Produce Lab**
- [ ] A text channel **#produce-check**
- [ ] Developer Mode turned on
- [ ] The channel's **CHANNEL_ID** (digits only) saved somewhere
- [ ] Your partner has joined the server

Next: [discord-bot-setup.md](discord-bot-setup.md).
