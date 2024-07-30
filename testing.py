import unittest


# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    # unittest.main()
    test = """
    shuffle_off
shuffle_on
prev_track
play
pause
next_track
repeat_context
repeat_track
repeat_off
add_queue
    """
    print(test.upper())