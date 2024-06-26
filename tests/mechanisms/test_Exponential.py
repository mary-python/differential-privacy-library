import numpy as np
from unittest import TestCase

from diffprivlib.mechanisms import Exponential


class TestExponential(TestCase):
    def setup_method(self, method):
        self.mech = Exponential

    def teardown_method(self, method):
        del self.mech

    def test_class(self):
        from diffprivlib.mechanisms import DPMechanism
        self.assertTrue(issubclass(Exponential, DPMechanism))

    def test_inf_epsilon(self):
        utility = [1, 0, 0, 0, 0]
        mech = self.mech(epsilon=float("inf"), utility=utility, sensitivity=1)

        for i in range(1000):
            self.assertEqual(mech.randomise(), 0)

    def test_zero_sensitivity(self):
        utility = [1, 0, 0, 0, 0]
        mech = self.mech(epsilon=1, utility=utility, sensitivity=0)

        for i in range(1000):
            self.assertEqual(mech.randomise(), 0)

    def test_nonzero_delta(self):
        utility = [1, 0, 0, 0, 0]
        mech = self.mech(epsilon=1, utility=utility, sensitivity=1)
        mech.delta = 0.1

        with self.assertRaises(ValueError):
            mech.randomise()

    def test_empty_utility(self):
        with self.assertRaises(ValueError):
            self.mech(epsilon=1, utility=[], sensitivity=1)

    def test_neg_sensitivity(self):
        with self.assertRaises(ValueError):
            self.mech(epsilon=1, utility=[1], sensitivity=-1)

    def test_monotonic(self):
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic=True))
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic=False))
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic=""))
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic="Hello"))
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic=[]))
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic=[1]))
        self.assertIsNotNone(self.mech(epsilon=1, utility=[1], sensitivity=1, monotonic=(1, 2, 3)))

    def test_wrong_input_types(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon=1j, utility=[1], sensitivity=1)

        with self.assertRaises(TypeError):
            self.mech(epsilon="1", utility=[1], sensitivity=1)

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=[1j], sensitivity=1)

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=["1"], sensitivity=1)

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=[1], sensitivity=1j)

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=[1], sensitivity="1")

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=(1), sensitivity=1)

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=[1], sensitivity=1, measure=(1))

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=[1], sensitivity=1, measure=[1j])

        with self.assertRaises(TypeError):
            self.mech(epsilon=1, utility=[1], sensitivity=1, candidates=(1))

    def test_wrong_arg_length(self):
        with self.assertRaises(ValueError):
            self.mech(epsilon=1, utility=[1, 2], sensitivity=1, candidates=[1, 2, 3])

        with self.assertRaises(ValueError):
            self.mech(epsilon=1, utility=[1, 2], sensitivity=1, candidates=[1])

        with self.assertRaises(ValueError):
            self.mech(epsilon=1, utility=[1, 2], sensitivity=1, measure=[1, 2, 3])

        with self.assertRaises(ValueError):
            self.mech(epsilon=1, utility=[1, 2], sensitivity=1, measure=[1])

    def test_non_none_input(self):
        mech = self.mech(epsilon=1, sensitivity=1, utility=[0, 1])

        with self.assertRaises(ValueError):
            mech.randomise(1)

    def test_correct_output_domain(self):
        mech = self.mech(epsilon=1, utility=[1, 0, 0, 0, 0], sensitivity=1)
        runs = 100

        for i in range(runs):
            self.assertTrue(0 <= mech.randomise() < 5)

        candidates = ["A", "B", "C", "D", "F"]
        mech = self.mech(epsilon=1, utility=[1, 0, 0, 0, 0], sensitivity=1, candidates=candidates)

        for i in range(runs):
            self.assertIn(mech.randomise(), candidates)

    def test_non_uniform_measure(self):
        measure = [1, 2, 1, 1]
        utility = [1, 1, 0, 0]
        runs = 20000
        mech = self.mech(epsilon=2 * np.log(2), utility=utility, measure=measure, sensitivity=1, random_state=0)
        count = [0] * 4

        for i in range(runs):
            count[mech.randomise()] += 1

        self.assertAlmostEqual(count[1] / count[0], 2, delta=0.1)

    def test_zero_measure(self):
        measure = [1, 1, 0]
        utility = [1, 1, 1]
        runs = 10000
        mech = self.mech(epsilon=1, utility=utility, measure=measure, sensitivity=1, random_state=0)
        count = [0] * 3

        for i in range(runs):
            count[mech.randomise()] += 1

        self.assertEqual(count[2], 0)
        self.assertAlmostEqual(count[0], count[1], delta=runs*0.03)

    def test_inf_utility_measure(self):
        list_with_inf = [1, 0, float("inf")]

        self.assertRaises(ValueError, self.mech, epsilon=1, utility=list_with_inf, sensitivity=1)
        self.assertRaises(ValueError, self.mech, epsilon=1, utility=[1] * 3, measure=list_with_inf, sensitivity=1)

        self.assertRaises(ValueError, self.mech, epsilon=1, utility=[-val for val in list_with_inf], sensitivity=1)
        self.assertRaises(ValueError, self.mech, epsilon=1, utility=[1] * 3, measure=[-val for val in list_with_inf],
                          sensitivity=1)

    def test_distrib_prob(self):
        epsilon = np.log(2)
        runs = 2000
        rng = np.random.RandomState(42)
        mech1 = self.mech(epsilon=epsilon, utility=[2, 1, 0], sensitivity=1, monotonic=False, random_state=rng)
        mech2 = self.mech(epsilon=epsilon, utility=[2, 1, 1], sensitivity=1, monotonic=False, random_state=rng)
        counts = np.zeros((2, 3))

        for i in range(runs):
            counts[0, mech1.randomise()] += 1
            counts[1, mech2.randomise()] += 1

        for vec in counts.T:
            # print(vec.max() / vec.min())
            self.assertLessEqual(vec.max() / vec.min(), np.exp(epsilon) + 0.1)

    def test_monotonic_distrib(self):
        epsilon = np.log(2)
        runs = 2000
        rng = np.random.RandomState(42)
        mech1 = self.mech(epsilon=epsilon, utility=[2, 1, 0], sensitivity=1, monotonic=True, random_state=rng)
        mech2 = self.mech(epsilon=epsilon, utility=[2, 1, 1], sensitivity=1, monotonic=True, random_state=rng)
        counts = np.zeros((2, 3))

        for i in range(runs):
            counts[0, mech1.randomise()] += 1
            counts[1, mech2.randomise()] += 1

        for vec in counts.T:
            self.assertLessEqual(vec.max() / vec.min(), np.exp(epsilon) + 0.1)

    def test_random_state(self):
        mech1 = self.mech(epsilon=1, utility=[2, 1, 0], sensitivity=1, random_state=42)
        mech2 = self.mech(epsilon=1, utility=[2, 1, 0], sensitivity=1, random_state=42)
        self.assertEqual([mech1.randomise() for _ in range(100)], [mech2.randomise() for _ in range(100)])

        self.assertNotEqual([mech1.randomise()] * 100, [mech1.randomise() for _ in range(100)])

        mech2 = self.mech(epsilon=1, utility=[2, 1, 0], sensitivity=1, random_state=np.random.RandomState(0))
        self.assertNotEqual([mech1.randomise() for _ in range(100)], [mech2.randomise() for _ in range(100)])

    def test_repr(self):
        repr_ = repr(self.mech(epsilon=1, utility=[1], sensitivity=1))
        self.assertIn(".Exponential(", repr_)

    def test_bias(self):
        self.assertRaises(NotImplementedError, self.mech(epsilon=1, utility=[1], sensitivity=1).bias, 0)

    def test_variance(self):
        self.assertRaises(NotImplementedError, self.mech(epsilon=1, utility=[1], sensitivity=1).variance, 0)
