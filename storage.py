from django.utils._os import safe_join
from django.utils.module_loading import import_string
from mighty.functions import setting, logger
import os

storage_default = "django.core.files.storage.FileSystemStorage"
storage_choice = setting("STORAGE", storage_default)
Storage = import_string(storage_choice)

"""
Override the storage to use a new storage capability without connection.
Usefull for local development and do not be impacted by requirements.

Also, the class duplicate the function save and remove that able you to backup or synchronate your data.
Usefull for cost service.
"""
class CloudStorage(Storage):
    def __init__(self, **settings):
        todel = [name for name, value in settings.items() if not hasattr(self, name)]
        logger("mighy", "debug", "CloudStorage: delete settings: %s" % todel)
        for field in todel: del settings[field]
        super().__init__(**settings)

if storage_choice != storage_default:
    class CloudStorage(CloudStorage):
        def _save_backup(self, name, content):
            content.seek(0)
            filename = "%s/%s" % (setting("MEDIA_ROOT"), name)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as bacfile:
                while True:
                    buf=content.read(1024)
                    if buf: 
                        for byte in buf:
                            pass
                        n=bacfile.write(buf)
                    else:
                        break
        
        # Backup file in localstorage
        def _save(self, name, content, headers=None):
            original_name = super(CloudStorage, self)._save(name, content, headers=None)
            self._save_backup(name, content)
            return original_name

        # Remove a directory empty
        def remove_dir(self, name):
            dirname = os.path.dirname(name)
            level = 1
            if os.path.isdir(dirname):
                while not os.listdir(dirname):
                    if level <= 5:
                        os.rmdir(dirname)
                        dirname = os.path.dirname(dirname)
                        level += 1
                    else:
                        break

        # Delete the backup file
        def delete_backup(self, name):
            name = "%s/%s" % (setting("MEDIA_ROOT"), name)
            assert name, "The name argument is not allowed to be empty."
            name = os.path.realpath(name)
            try:
                if os.path.isdir(name):
                    os.rmdir(name)
                else:
                    os.remove(name)
            except FileNotFoundError:
                pass
            self.remove_dir(name)

        def delete(self, name):
            super(CloudStorage, self).delete(name)
            self.delete_backup(name)