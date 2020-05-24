from .helpers import IFPTestCase
from intficpy.thing_base import Thing
from intficpy.things import Surface, Container, Lock, UnderSpace


class TestDesc(IFPTestCase):
    def test_room_desc_contains_description_of_described_item_in_room(self):
        subject = Thing(self._get_unique_noun())
        subject.description = (
            f"A very large, very strange {subject.verbose_name} lurks in the corner."
        )
        self.start_room.addThing(subject)
        self.game.turnMain(f"l")
        msg = self.app.print_stack.pop()
        self.assertIn(subject.description, msg)

    def test_desc_contains_contents_if_desc_reveal(self):
        subject = Surface(self._get_unique_noun(), self.game)
        subject.desc_reveal = True
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"l")
        msg = self.app.print_stack.pop()
        self.assertIn(content.verbose_name, msg)

    def test_xdesc_does_not_contain_contents_if_not_xdesc_reveal(self):
        subject = Surface(self._get_unique_noun(), self.game)
        subject.xdesc_reveal = False
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(content.verbose_name, msg)

    def test_desc_does_not_contain_contents_if_lid_is_closed(self):
        subject = Container(self._get_unique_noun(), self.game)
        subject.giveLid()
        subject.is_open = False
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(content.verbose_name, msg)

    def test_desc_contains_lid_state(self):
        subject = Container(self._get_unique_noun(), self.game)
        subject.giveLid()
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        subject.is_open = False
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertIn("is closed", msg)

    def test_desc_contains_lock_state(self):
        subject = Container(self._get_unique_noun(), self.game)
        subject.giveLid()
        lock = Lock(False, None)
        subject.setLock(lock)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn("is locked", msg)

    def test_contains_list_does_not_contain_composite_child_items(self):
        subject = Container(self._get_unique_noun(), self.game)
        content = Thing(self._get_unique_noun())
        child = Thing("child")
        content.addComposite(child)
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(child.verbose_name, msg)

    def test_undescribed_underspace_not_included_in_composite_desc(self):
        subject = Thing(self._get_unique_noun())
        child = UnderSpace("child", self.game)
        subject.addComposite(child)
        self.start_room.addThing(subject)

        self.assertNotIn(child.verbose_name, subject.composite_desc)

        self.game.turnMain(f"l {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(child.verbose_name, msg)
