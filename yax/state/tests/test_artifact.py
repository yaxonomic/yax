import unittest
import os
from yax.state.type import Artifact


class TestArtifact(unittest.TestCase):

    def test_declare(self):
        artifact = Artifact.declare(dir_="/test/dir/", module_id=0)
        self.assertEqual(artifact.data_dir, "/test/dir/")
        self.assertEqual(artifact.module_id, 0)
        self.assertEqual(isinstance(artifact, Artifact), True)

    def test_is_complete(self):
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        complete_art_dir = os.path.join(directory, "data",
                                        "complete_test_artifact")
        incomplete_art_dir = os.path.join(directory, "data",
                                          "incomplete_test_artifact")
        complete_artifact = Artifact.declare(dir_=complete_art_dir,
                                             module_id=0)
        incomplete_artifact = Artifact.declare(dir_=incomplete_art_dir,
                                               module_id=1)

        self.assertTrue(complete_artifact)
        self.assertTrue(complete_artifact.is_complete)
        self.assertEqual(complete_artifact._get_complete_flag_path(),
                         os.path.join(complete_art_dir, ".complete"))

        self.assertFalse(incomplete_artifact)
        self.assertFalse(incomplete_artifact.is_complete)
        self.assertEqual(incomplete_artifact._get_complete_flag_path(),
                         os.path.join(incomplete_art_dir, ".complete"))

    def test_complete(self):
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        incomplete_art_dir = os.path.join(directory, "data",
                                          "incomplete_test_artifact")

        incomplete_artifact = Artifact.declare(dir_=incomplete_art_dir,
                                               module_id=1)

        self.assertFalse(incomplete_artifact)
        self.assertFalse(incomplete_artifact.is_complete)
        self.assertEqual(incomplete_artifact._get_complete_flag_path(),
                         os.path.join(incomplete_art_dir, ".complete"))

        incomplete_artifact.complete()

        self.assertTrue(incomplete_artifact)
        self.assertTrue(incomplete_artifact.is_complete)

        os.remove(incomplete_artifact._get_complete_flag_path())

    def test_final_output(self):
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        final_artifact_dir = os.path.join(directory, "data",
                                          "final_test_artifact")
        complete_artifact_dir = os.path.join(directory, "data",
                                             "complete_test_artifact")
        incomplete_artifact_dir = os.path.join(directory, "data",
                                               "incomplete_test_artifact")
        final_artifact = Artifact.declare(dir_=final_artifact_dir, module_id=0)
        complete_artifact = Artifact.declare(dir_=complete_artifact_dir,
                                             module_id=1)
        incomplete_artifact = Artifact.declare(dir_=incomplete_artifact_dir,
                                               module_id=1)

        self.assertTrue(final_artifact.is_final_output())
        self.assertFalse(complete_artifact.is_final_output())
        self.assertFalse(incomplete_artifact.is_final_output())
