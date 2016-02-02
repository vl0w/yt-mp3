import env, os
from tagger import TagArchive

def make_symlinks(parser_env: env.ParserEnvironment):
    parser_env.log.info("Making MP3 Symlinks")

    music_files = parser_env.load_downloaded_music_files()
    tag_archive = TagArchive(parser_env.file_tagarchive)
    for music_file in music_files:
        if not tag_archive.is_already_tagged(music_file):
            parser_env.log.warning("Music file is not tagged and therefore no symlink can be created")
            continue

        description = parser_env.sync_description_for_video_id(music_file)

        path_target_directory = "{0}{1}".format(parser_env.path_main, description.target_directory_name)

        if not os.path.isdir(path_target_directory):
            os.mkdir(path_target_directory)

        tags = music_file.read_tags()
        file_symlink = "{0}/{1} - {2}.mp3".format(path_target_directory, tags.artist.replace("/","-"), tags.title.replace("/", " "))

        if not os.path.isfile(file_symlink):
            os.symlink(music_file.file_mp3, file_symlink)

    parser_env.log.info("Symlinks updated")