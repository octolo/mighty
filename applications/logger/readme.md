# Logger
The logger application allows you to extend logging facilities.

## Handler
You can user some handler from the mighty.logger application.

    from mighty.applications.logger import handlers

- ConsoleHandler, like runserver log
- FileHandler, like logging.handlers.FileHandler
- DatabaseHander, in working

Now you should be found a **logs** button next to the history button in the view change form.

# Model Log
Like the previous, you are able to add a logger on your model. But the log use the logging method and there attributes. it is to keep the events that you deem necessary.

This facility do not need an extrem configuration. If you use a mighty handler, all you need it is to send an extra argument **log_in_db** that contain your model.

    logger.info('my message', extra={'log_in_db': self.request.user})

To check about the events you also need to add an heritage in your modelAdmin.


    from mighty.applications.logger.admin import ModelWithLogAdmin

    class UserAdmin(admin.modelAdmin, ModelWithLogAdmin):
        pass    from myapps.models import Model
        from mighty.applications.logger.admin import ModelWithLogAdmin

        @register.admin(Model)
        class ModelAdmin(admin.modelAdmin, ModelWithLogAdmin):
        pass

Now you should be found a **logs** button next to the history button in the view change form.
