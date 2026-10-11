import unittest

from scripts.export_production_assets import parse_scene_block


class ProductionManifestParserTests(unittest.TestCase):
    def test_parses_multiline_scene_fields(self):
        block = """IMAGE PROMPT: Ancient Ayodhya at sunrise.
Keep Rama's face consistent.
MOTION PROMPT:
- 0-3s: Slow camera push-in.
- 3-6s: Flags move in the wind.
- 6-10s: Rama turns toward the palace.
DIALOGUE: రామా, సిద్ధంగా ఉండు.
LIP-SYNC: 0.5s-4s; close mouth after speech.
"""
        fields = parse_scene_block(block)
        self.assertIn("Ancient Ayodhya at sunrise.", fields["IMAGE PROMPT"])
        self.assertIn("Keep Rama's face consistent.", fields["IMAGE PROMPT"])
        self.assertIn("0-3s: Slow camera push-in.", fields["MOTION PROMPT"])
        self.assertIn("6-10s: Rama turns toward the palace.", fields["MOTION PROMPT"])
        self.assertEqual(fields["DIALOGUE"], "రామా, సిద్ధంగా ఉండు.")
        self.assertIn("close mouth after speech", fields["LIP-SYNC"])

    def test_empty_fields_are_not_fabricated(self):
        fields = parse_scene_block("IMAGE PROMPT: A forest at dusk.\nMOTION PROMPT:\n- 0-3s: Fog drifts.\n")
        self.assertTrue(fields["IMAGE PROMPT"])
        self.assertTrue(fields["MOTION PROMPT"])
        self.assertNotIn("DIALOGUE", fields)


if __name__ == "__main__":
    unittest.main()
