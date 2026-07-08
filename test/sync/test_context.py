import unittest

from morango.constants import transfer_stages
from morango.constants import transfer_statuses

from kolibri_sync_extras_plugin.sync.context import BackgroundSessionContext

from ..base import BaseTestCase


class SyncContextTestCase(BaseTestCase):
    def test_background_context(self):
        context = BackgroundSessionContext(transfer_session=self.transfer_session)
        self.assertTrue(context.is_server)
        self.assertTrue(context.is_receiver)
        context.update_state(stage=transfer_stages.QUEUING, stage_status=transfer_statuses.STARTED)
        self.transfer_session.update_state.assert_called_once()

    def test_is_server__derived_from_sync_session(self):
        self.sync_session.is_server = False
        context = BackgroundSessionContext(transfer_session=self.transfer_session)
        self.assertFalse(context.is_server)

    def test_is_server__explicit_kwarg_overrides_sync_session(self):
        self.sync_session.is_server = False
        context = BackgroundSessionContext(transfer_session=self.transfer_session, is_server=True)
        self.assertTrue(context.is_server)

    def test_is_receiver__server_push(self):
        # a server receiving a push is the receiver
        self.sync_session.is_server = True
        self.transfer_session.push = True
        context = BackgroundSessionContext(transfer_session=self.transfer_session)
        self.assertTrue(context.is_receiver)
        self.assertFalse(context.is_producer)

    def test_is_receiver__server_pull(self):
        # a server servicing a pull is the producer, not the receiver
        self.sync_session.is_server = True
        self.transfer_session.push = False
        context = BackgroundSessionContext(transfer_session=self.transfer_session)
        self.assertFalse(context.is_receiver)
        self.assertTrue(context.is_producer)

    def test_is_receiver__client_push(self):
        # a client pushing is the producer, not the receiver
        self.sync_session.is_server = False
        self.transfer_session.push = True
        context = BackgroundSessionContext(transfer_session=self.transfer_session)
        self.assertFalse(context.is_receiver)
        self.assertTrue(context.is_producer)

    @unittest.expectedFailure
    def test_is_receiver__client_pull(self):
        # a client pulling is the receiver, not the producer
        # currently fails because morango's SessionContext resolves `is_push` via
        # `transfer_session.push or self.is_push`, which collapses `False` (pull) down to
        # `None` when no explicit `is_push` is passed, since nothing set `self.is_push` first.
        # remove this xfail marker once that's fixed upstream in morango.
        self.sync_session.is_server = False
        self.transfer_session.push = False
        context = BackgroundSessionContext(transfer_session=self.transfer_session)
        self.assertTrue(context.is_receiver)
        self.assertFalse(context.is_producer)
