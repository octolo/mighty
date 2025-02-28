import subprocess

from mighty.thumbnail.thumbnail import ThumbnailBackend


class ThumbnailBackend(ThumbnailBackend):
    convert = '/bin/convert'
    opt_thumbnail = '-thumbnail'
    opt_thumbnail2 = '"124^>"'
    opt_background = '-background'
    opt_background2 = 'white'
    opt_alpha = '-alpha'
    opt_alpha2 = 'remove'
    opt_crop = '-crop'
    opt_crop2 = '124x175+0+0'
    opt_png = 'PNG:-'
    pipe_base64 = '|'
    pipe_base642 = 'base64'

    @property
    def command(self):
        return ' '.join([
            self.convert,
            self.opt_thumbnail,
            self.opt_thumbnail2,
            self.opt_background,
            self.opt_background2,
            self.opt_alpha,
            self.opt_alpha2,
            self.opt_crop,
            self.opt_crop2,
            self.element._file.temporary_file_path() + '[0]',
            self.opt_png,
            self.pipe_base64,
            self.pipe_base642,
        ])

    @property
    def base64(self):
        process = subprocess.Popen(
            [self.command],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if not stderr:
            return stdout.decode()
        raise Exception(stderr)
