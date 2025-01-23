import asyncio
import discord
from discord.ext import commands, tasks
import os
import git  # GitPython for managing the repository
import re  # Regex for sanitizing file names
import github

intents = discord.Intents.default()  # Create intents
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    if not auto_push.is_running():  # Check if the task is already running
        auto_push.start()  # Start the background task to auto-push


# Function to sanitize file names
def sanitize_filename(filename):
    # Remove invalid characters and limit length
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)  # Remove invalid characters
    return sanitized[:255]  # Ensure the name isn't too long


@bot.command(name='meme', aliases=['memes'])
async def download_media(ctx):
    channel = ctx.channel
    downloaded_files = set()

    # Create the "media" folder if it doesn't exist
    if not os.path.exists('media'):
        os.makedirs('media')

    print(f"Processing messages in channel: {channel.name}")  # Debug statement

    # Iterate over messages in the channel
    async for message in channel.history(limit=None):
        for attachment in message.attachments:
            if attachment.filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.mov')):  # Add more formats as needed
                # Sanitize the file name
                sanitized_filename = sanitize_filename(attachment.filename)
                file_path = os.path.join('media', sanitized_filename)

                if file_path not in downloaded_files and not os.path.exists(file_path):  # Check if the file already exists
                    try:
                        await attachment.save(file_path)
                        downloaded_files.add(file_path)
                        print(f"Downloaded {sanitized_filename}")
                    except OSError as e:
                        print(f"Failed to save file {sanitized_filename}: {e}")
                else:
                    print(f"Skipped {sanitized_filename}, already exists.")

@bot.command(name='save')
async def save_messages(ctx):
    # Get the server (guild) from the context
    guild = ctx.guild

    # Create a directory to save the messages if it doesn't exist
    if not os.path.exists('saved_messages'):
        os.makedirs('saved_messages')

    # Iterate through all the channels in the guild
    for channel in guild.text_channels:
        # Create a file for each channel
        file_path = os.path.join('saved_messages', f'{channel.name}.txt')

        try:
            # Attempt to fetch the message history for the channel
            async with channel.typing():  # Optional: Show typing indicator
                with open(file_path, 'w', encoding='utf-8') as f:
                    async for message in channel.history(limit=None):
                        f.write(f'[{message.created_at}] {message.author}: {message.content}\n')

            print(f'Saved messages from {channel.name} to {file_path}')

        except discord.Forbidden:
            # Handle the case where the bot lacks permissions
            print(f"Skipping channel {channel.name}: Missing access.")
        except Exception as e:
            # Handle any other exceptions
            print(f"An error occurred while saving messages from {channel.name}: {e}")

    await ctx.send("All accessible messages have been saved")

@bot.command(name='update') 
async def manual_update(ctx):
    # Manually update the GitHub repository with changes in the media folder.
    try:
        await push_to_git(ctx)  # Pass ctx to the push_to_git function
        await ctx.send("Successfully updated the GitHub repository with the latest changes.")
    except Exception as e:
        await ctx.send(f"Failed to update the GitHub repository. Error: {e}")

@bot.command(name='list')
async def list_files(ctx):
    #Lists the number of files in the media folder.
    media_folder = './media'

    if not os.path.exists(media_folder):
        await ctx.send("The media folder does not exist.")
        return

    file_count = sum(len(files) for _, _, files in os.walk(media_folder))
    await ctx.send(f"There are {file_count} files in the media folder.")

@bot.command(name='push')
async def push_to_git(ctx):  # Add ctx parameter
    try:
        from github import Github

        # Replace with your personal access token
        g = Github("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")

        # Specify the repository name
        repo_name = "zanarian1o1/a-collection-of-memes"
        repo = g.get_repo(repo_name)

        # Path to the local media folder
        local_media_folder = './media'

        # Ensure the media folder exists locally
        if not os.path.exists(local_media_folder):
            await ctx.send(f"Media folder '{local_media_folder}' does not exist. Aborting push.")
            return

        # Iterate through files in the media folder and push them to GitHub
        for root, _, files in os.walk(local_media_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                repo_file_path = os.path.relpath(local_file_path, local_media_folder)

                # Read the content of the file asynchronously
                file_content = await asyncio.to_thread(read_file, local_file_path)

                try:
                    # Check if the file already exists in the repo
                    contents = await asyncio.to_thread(repo.get_contents, f"media/{repo_file_path}", ref="main")

                    # Update the file if it exists
                    await asyncio.to_thread(repo.update_file, contents.path, f"Update {repo_file_path}", file_content, contents.sha, branch="main")
                    print(f"Updated {repo_file_path} in the repository.")
                except github.GithubException as e:
                    if e.status == 404:
                        # File does not exist, create it
                        await asyncio.to_thread(repo.create_file, f"media/{repo_file_path}", f"Add {repo_file_path}", file_content, branch="main")
                        print(f"Added {repo_file_path} to the repository.")
                    else:
                        # Handle other GitHub API errors
                        print(f"GitHub API error: {e}")
                        await ctx.send(f"GitHub API error: {e}")

        await ctx.send("All files in the media folder have been pushed to the repository.")

    except Exception as e:
        print(f"Unexpected error during GitHub operations: {e}")
        await ctx.send(f"Unexpected error during GitHub operations: {e}")

def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

@tasks.loop(minutes=10)  # Automatically push every 10 minutes
async def auto_push():
    if os.path.exists('media'):  # Ensure the media folder exists
        try: 
            repo = git.Repo('./a-collection-of-memes')

            # Check if there are any uncommitted changes in the media folder
            uncommitted_files = [
                item.a_path for item in repo.index.diff(None) if item.a_path.startswith('media/')
            ]
            if uncommitted_files:
                print(f"Detected changes in 'media' folder: {uncommitted_files}. Pushing updates...")
                await push_to_git()
            else:
                print("No changes detected in the 'media' folder.")
        except git.exc.GitCommandError as e:
            print(f"Git error during auto-push: {e}")
        except Exception as e:
            print(f"Unexpected error during auto-push: {e}")

@bot.command(name='freaky')
async def freaky_command(ctx):
    user_name = ctx.author.name  # Get the name of the user who sent the command
    await ctx.send(f"Why the hell do you want this command {user_name}?")

bot.run('bot token') # Replace with your actual bot token
