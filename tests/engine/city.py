from engine.engine import Engine
from common.models import DummyRequest

TEST_UID = 1


class TestCityUnits(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(DummyRequest(TEST_UID))
        self.engine.start()

    def tearDown(self):
        pass

    def testMoveUnits1(self):
        post = {

        }

        self.assertTrue(self.engine.city.id)
        self.assertTrue(self.engine.city.move_units(post))
