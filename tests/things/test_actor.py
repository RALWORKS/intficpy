from ..helpers import IFPTestCase
from intficpy.actor import Actor
from intficpy.thing_base import Thing


class TestActorInventoryDescription(IFPTestCase):
    def setUp(self):
        super().setUp()

        self.actor = Actor(self.game, "girl")
        self.item = Thing(self.game, "item")
        self.item.moveTo(self.actor)

    def test_actor_desc_does_not_include_inventory(self):
        self.assertNotIn(self.actor.desc, self.item.verbose_name)

    def test_actor_xdesc_does_not_include_inventory(self):
        self.assertNotIn(self.actor.xdesc, self.item.verbose_name)
