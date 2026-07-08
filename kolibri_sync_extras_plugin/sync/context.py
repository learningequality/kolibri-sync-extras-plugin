from morango.sync.context import LocalSessionContext


class BackgroundSessionContext(LocalSessionContext):
    """
    Background session context class that won't trigger our BackgroundFinalizeJobOperation when we
    run sync operations in the background. This inherits LocalSessionContext so the default Morango
    operations will accept this context
    """

    def __init__(self, *args, **kwargs):
        is_server = kwargs.pop("is_server", None)
        super(BackgroundSessionContext, self).__init__(*args, **kwargs)
        # base class sets `is_server` on the presence of a request object, which we don't have in bg,
        # so we rely on it being passed in, deferring to the sync session if not provided
        if is_server is None:
            is_server = getattr(self.sync_session, "is_server", False)
        self.is_server = is_server
