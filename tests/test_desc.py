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
        subject = Surface(self._get_unique_noun())
        subject.desc_reveal = True
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"l")
        msg = self.app.print_stack.pop()
        self.assertIn(content.verbose_name, msg)

    def test_xdesc_does_not_contain_contents_if_not_xdesc_reveal(self):
        subject = Surface(self._get_unique_noun())
        subject.xdesc_reveal = False
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(content.verbose_name, msg)

    def test_desc_does_not_contain_contents_if_lid_is_closed(self):
        subject = Container(self._get_unique_noun())
        subject.giveLid()
        subject.is_open = False
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(content.verbose_name, msg)

    def test_desc_contains_lid_state(self):
        subject = Container(self._get_unique_noun())
        subject.giveLid()
        content = Thing(self._get_unique_noun())
        subject.addThing(content)
        self.start_room.addThing(subject)
        subject.is_open = False
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertIn("is closed", msg)

    def test_desc_contains_lock_state(self):
        subject = Container(self._get_unique_noun())
        subject.giveLid()
        lock = Lock(False, None)
        subject.setLock(lock)
        self.game.turnMain(f"x {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn("is locked", msg)

    def test_contains_list_does_not_contain_composite_child_items(self):
        subject = Container(self._get_unique_noun())
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
        child = UnderSpace("child")
        subject.addComposite(child)
        self.start_room.addThing(subject)

        self.assertNotIn(child.verbose_name, subject.composite_desc)

        self.game.turnMain(f"l {subject.verbose_name}")
        msg = self.app.print_stack.pop()
        self.assertNotIn(child.verbose_name, msg)


class TestPlural(IFPTestCase):
    def test_plural_of_plural_returns_verbose_name(self):
        subject = Thing("beads")
        subject.is_plural = True
        self.assertEqual(subject.verbose_name, subject.plural)

    def test_desc_of_plural_conjugates_correctly(self):
        subject = Thing("beads")
        self.assertNotIn("are", subject.desc)
        subject.is_plural = True
        self.assertIn("are", subject.desc)

    def test_plural_uses_special_plural(self):
        subject = Thing("fungus")
        subject.special_plural = "fungi"
        self.assertEqual(subject.plural, subject.special_plural)


class TestVerboseName(IFPTestCase):
    def test_verbose_name_contains_all_adjectives_in_order_if_not_overridden(self):
        subject = Thing("flower")
        ADJECTIVES = ["grandma's", "big", "bright", "yellow"]
        subject.setAdjectives(ADJECTIVES)
        expected_name = " ".join(ADJECTIVES + [subject.name])
        self.assertEqual(expected_name, subject.verbose_name)

    def test_verbose_name_is__verbose_name_if_overridden(self):
        subject = Thing("flower")
        ADJECTIVES = ["grandma's", "big", "bright", "yellow"]
        subject.setAdjectives(ADJECTIVES)
        NAME = "sasquatch"
        subject._verbose_name = NAME
        self.assertEqual(NAME, subject.verbose_name)
