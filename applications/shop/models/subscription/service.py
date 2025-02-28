class Service:
    def has_service(self, service):
        return self.has_cache_field(service.lower())

    def set_on_use_count(self):
        self.one_use_count = self.offer.frequency == 'ONUSE'

    def set_subscription(self):
        if hasattr(self.group_or_user, 'subscription'):
            self.group_or_user.subscription = self
            self.group_or_user.save()

    def set_cache_service(self):
        if self.offer:
            for service in self.offer.service.all():
                self.add_cache(service.name.lower(), service.code)
