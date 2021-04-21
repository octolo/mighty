from mighty.management import ModelBaseCommand
from os import listdir, walk
from os.path import isfile, join

class Command(ModelBaseCommand):
    model = "Missive"
    label = "Mighty"
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--spool_path', default="/var/spool/postfix")
        parser.add_argument('--status_parse_dir', default="defer,bounce")

    def handle(self, *args, **options):
        self.spool_path = options.get('spool_path')
        self.status_parse_dir = options.get('status_parse_dir')
        self.mail_parse_dir = options.get('mail_parse_dir')
        super().handle(*args, **options)

    def get_queryset(self):
        files = []
        for d in self.status_parse_dir.split(','):
            mypath = join(self.spool_path, d)
            for (dirpath, dirnames, filenames) in walk(mypath):
                for f in filenames:
                    files.append({"dir": d, "name": f, "path": join(dirpath, f)})

            #for f in listdir(mypath):
            #    if isfile(join(mypath, f)):
        return files

    def on_object(self, obj):
        status = "get_%s" % obj["dir"]
        if hasattr(self, status) and callable(getattr(self, status)):
            getattr(self, status)(obj)

    def get_defer_message_id(self, obj):
        deferred_path = join(self.spool_path, "deferred")
        for (dirpath, dirnames, filenames) in walk(deferred_path):
            for f in filenames:
                if f == obj["name"]:
                    deferred_path = join(dirpath, obj["name"])
                    print(deferred_path)
                    with open(deferred_path, "r") as source_file:
                        import re
                        print(re.search("Message-ID: ND (<.*>)", source_file.read(), re.MULTILINE).group(1))
                    break
        return True

    def get_defer(self, obj):
        message_id = self.get_defer_message_id(obj)
        
        #with open(obj["file"], "r") as trace_file:
        #    trace = trace_file.read()
        #    #if trace:
        #    #    print(trace)



    