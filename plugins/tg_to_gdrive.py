import os
import pathlib
import time
import pyrogram
from bot import logger
from helper_funcs import gdriveTools
from helper_funcs.bot_utils import *
from helper_funcs.display_progress import progress_for_pyrogram
from translation import Translation
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client as app
from config import Config
from helper_funcs.fsub import handle_force_sub

@app.on_message(filters.media & filters.private & filters.incoming)
async def tg_to_gdrive_upload(bot, update):
    back = await handle_force_sub(bot, update)
    if back == 400:
        return
    download_location = Config.DOWNLOAD_LOCATION + "/"
    reply_message = await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DOWNLOAD_START,
        reply_to_message_id=update.message_id
    )
    c_time = time.time()
    try:
           the_real_download_location = await bot.download_media(
            message=update,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                reply_message,
                c_time
            )
        )
    except Exception as e:
        logger.error(str(e))
    if the_real_download_location is None:
        return await reply_message.edit_text("File Download Failed")
    try:
        await bot.edit_message_text(
            text=Translation.SAVED_RECVD_DOC_FILE,
            chat_id=update.chat.id,
            message_id=reply_message.message_id
        )
    except:
        pass
    download_directory = the_real_download_location
    if os.path.exists(download_directory):
        up_name = pathlib.PurePath(download_directory).name
        size = get_readable_file_size(get_path_size(download_directory))
        try:
            await bot.edit_message_text(
                text="📥Download Completed!!!\nNow Uploading.",
                chat_id=reply_message.chat.id,
                message_id=reply_message.message_id
            )
        except Exception as e:
            logger.error(str(e))
        logger.info(f"Upload Name : {up_name}")
        drive = gdriveTools.GoogleDriveHelper(up_name)
        gd_url, index_url = drive.upload(download_directory)
        uri = str_to_b64(index_url)
        url = f"https://{Config.VIDEO_PLAYER_URL}/play?id={uri}"
        video = '.mp4', '.mkv', 'avi', '.ts', '.webm', '.flv', '.wmv', '.mov', '.gif'
        image = '.jpg', '.png', '.jpeg', 'webp'
        audio = '.mp3', '.m4a', '.ogg', '.wma', 'aac', 'wav' ,'flac'
        via = '.mp4', '.mkv', 'avi', '.ts', '.webm', '.flv', '.wmv', '.mov', '.gif', '.mp3', '.m4a', '.ogg', '.wma', 'aac', 'wav' ,'flac'
        forbid = 'xxx', 'sex', 'porn'
        if any(x in up_name.lower() for x in forbid):
            if update.from_user.id not in Config.AUTH_USERS:
                GENERATED = "You will be banned soon😈😈"
            else:
                GENERATED = f"<b>link Generated</b> \n\n<b>File:</b> [{up_name}]({index_url}) \n\n<b>Size:</b> {size}\n\n<b>Link:</b> [here]({url})"
        elif up_name.lower().endswith(via):
            GENERATED = f"<b>link Generated</b> \n\n<b>File:</b> [{up_name}]({index_url}) \n\n<b>Size:</b> {size}\n\n<b>Link:</b> [here]({url})"
        elif up_name.lower().endswith(image):
            GENERATED = f"<b>link Generated</b> \n\n<b>File:</b> [{up_name}]({index_url}) \n\n<b>Size:</b> {size}\n\n<b>Link:</b> [here]({url})\n\nI don't think you want to open image on website."
        else:
            GENERATED = f"<b>Link Generated</b> \n\n<b>File:</b> [{up_name}]({index_url}) \n\n<b>Size:</b> {size}"
        buttons = [[InlineKeyboardButton(text="Download", url=index_url)]]
        if up_name.lower().endswith(video):
            buttons.append([InlineKeyboardButton(text="Stream Video", url=url)])
        elif up_name.lower().endswith(image):
            buttons.append([InlineKeyboardButton(text="Open Image On Website", url=url)])
        elif up_name.lower().endswith(audio):
            buttons.append([InlineKeyboardButton(text="Stream Audio", url=url)])
        button_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(
        text=GENERATED,
        chat_id=update.chat.id,
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True,
        reply_markup=button_markup)
    try:
        os.remove(download_directory)
    except:
        pass
    await reply_message.delete()
