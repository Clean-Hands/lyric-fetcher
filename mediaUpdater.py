# adapted from https://stackoverflow.com/a/66037406

import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

async def get_media_info_helper():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:  # there needs to be a media session running
        info = await current_session.try_get_media_properties_async()

        # song_attr[0] != '_' ignores system attributes
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

        # converts winsdk vector to list
        info_dict['genres'] = list(info_dict['genres'])

        return info_dict
    # else:
    #     return 0

def get_media_info():
    return asyncio.run(get_media_info_helper())

