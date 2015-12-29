from os import listdir, remove
from os.path import isfile, isdir, join


def delete_orpahned_items(env):
    channels = env.read_channels()

    for channel in channels:
        env.log.info("Searching for orphaned items in channel {0}".format(channel.identification))
        synced_ids = channel.get_all_synchronized_video_ids()
        env.log.debug("Found {0} synced videos in archive".format(len(synced_ids)))

        # Get all downloaded mp3 files which do not contain a synced id in it's name
        orphaned_mp3_files = []
        if isdir(channel.download_path):
            for filename in listdir(channel.download_path):
                if isfile(join(channel.download_path, filename)) and filename.endswith("mp3"):
                    orphaned = True
                    for synced_id in synced_ids:
                        if synced_id in filename:
                            orphaned = False
                            break

                    if orphaned:
                        orphaned_mp3_files.append(join(channel.download_path, filename))

        # Remove all orphaned files
        if len(orphaned_mp3_files) > 0:
            env.log.info(
                "Deleting {0} orphaned items for channel {1}".format(len(orphaned_mp3_files), channel.identification))
            for orphaned_file in orphaned_mp3_files:
                remove(orphaned_file)
                env.log.debug("Deleted orphaned file {0}".format(orphaned_file))
