#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright 2024, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the California Institute of
#  Technology.  This software is subject to U.S. export control laws and regulations
#  and has been classified as EAR99.  By accepting this software, the user agrees to
#  comply with all applicable U.S. export laws and regulations.  User has the
#  responsibility to obtain export licenses, or other export authority as may be
#  required before exporting such information to foreign countries or providing
#  access to foreign persons.
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from unittest import TestCase

from ideas_api.lib.job_management.job_constants import JobConstants
from ideas_api.lib.processes.ogc_process_stages import OgcProcessStages


class TestOgcProcessStages(TestCase):
    def test_01(self):
        wrong_process_def = {
        }
        with self.assertRaises(ValueError):
            OgcProcessStages().setup(wrong_process_def)
        wrong_process_def = {
            'additionalParameters': {}
        }
        with self.assertRaises(ValueError):
            OgcProcessStages().setup(wrong_process_def)
        wrong_process_def = {
            'additionalParameters': {
                'parameters': []
            }
        }
        with self.assertRaises(ValueError):
            OgcProcessStages().setup(wrong_process_def)
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    }
                ]
            }
        }
        with self.assertRaises(ValueError) as cm:
            OgcProcessStages().setup(wrong_process_def)
        self.assertTrue('missing key-value pair: stage001Names' in str(cm.exception), f'wrong err msg: {cm.exception}')
        self.assertTrue('missing key-value pair: stage002Names' in str(cm.exception), f'wrong err msg: {cm.exception}')
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["LIS"]
                    }
                ]
            }
        }
        with self.assertRaises(ValueError) as cm:
            OgcProcessStages().setup(wrong_process_def)
        self.assertTrue('missing key-value pair: stage002Names' in str(cm.exception), f'wrong err msg: {cm.exception}')
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["LIS"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["LIS", "RAPID"]
                    }
                ]
            }
        }
        with self.assertRaises(ValueError) as cm:
            OgcProcessStages().setup(wrong_process_def)
        self.assertTrue('duplicate sub_process_name' in str(cm.exception), f'wrong error msg: {cm.exception}')
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": []
                    },
                    {
                        "name": "stage002Names",
                        "value": ["LIS", "RAPID"]
                    }
                ]
            }
        }
        with self.assertRaises(ValueError):
            OgcProcessStages().setup(wrong_process_def)
        return

    def test_02(self):
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["LIS"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["RRR", "RAPID"]
                    }
                ]
            }
        }
        ogc_process_stages = OgcProcessStages().setup(wrong_process_def)
        self.assertEqual("LIS", ogc_process_stages.get_next_process(JobConstants.PRE_PROCESSED, [True, True]))
        self.assertEqual("RRR", ogc_process_stages.get_next_process("LIS", [True, True]))
        self.assertEqual("RAPID", ogc_process_stages.get_next_process("RRR", [True, True]))
        self.assertEqual(JobConstants.FINISHED, ogc_process_stages.get_next_process("RAPID", [True, True]))
        return

    def test_03(self):
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["LIS", "POWER"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["RRR", "RAPID"]
                    }
                ]
            }
        }
        ogc_process_stages = OgcProcessStages().setup(wrong_process_def)
        self.assertEqual("LIS", ogc_process_stages.get_next_process(JobConstants.PRE_PROCESSED, [True, True]))
        self.assertEqual("POWER", ogc_process_stages.get_next_process("LIS", [True, True]))
        self.assertEqual("RRR", ogc_process_stages.get_next_process("POWER", [True, True]))
        self.assertEqual("RAPID", ogc_process_stages.get_next_process("RRR", [True, True]))
        self.assertEqual(JobConstants.FINISHED, ogc_process_stages.get_next_process("RAPID", [True, True]))
        return

    def test_04(self):
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["LIS", "POWER"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["RRR", "RAPID"]
                    }
                ]
            }
        }
        ogc_process_stages = OgcProcessStages().setup(wrong_process_def)
        with self.assertRaises(ValueError) as cm:
            ogc_process_stages.get_next_process("ABC", [True, True])
        self.assertTrue('missing sub_process' in str(cm.exception), f'wrong err msg: {cm.exception}')
        return

    def test_05(self):
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["LIS", "POWER"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["RRR", "RAPID"]
                    }
                ]
            }
        }
        ogc_process_stages = OgcProcessStages().setup(wrong_process_def)
        start, end = ogc_process_stages.get_process_range('POWER')
        self.assertEqual(start, 26)
        self.assertEqual(end, 50)
        return

    def test_06(self):
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["2"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["T1", "T2", "T3"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["S1", "S2", "S3", "S4", "S5", "S6"]
                    }
                ]
            }
        }
        ogc_process_stages = OgcProcessStages().setup(wrong_process_def)
        start, end = ogc_process_stages.get_process_range('S2')
        self.assertEqual(start, 45)
        self.assertEqual(end, 55)
        return

    def test_07(self):
        wrong_process_def = {
            'additionalParameters': {
                'parameters': [
                    {
                        "name": "stagesCount",
                        "value": ["3"]
                    },
                    {
                        "name": "stage001Names",
                        "value": ["T1", "T2"]
                    },
                    {
                        "name": "stage002Names",
                        "value": ["S1"]
                    },
                    {
                        "name": "stage003Names",
                        "value": ["P1", "P2", "P3", "P4"]
                    }
                ]
            }
        }
        ogc_process_stages = OgcProcessStages().setup(wrong_process_def)
        start, end = ogc_process_stages.get_process_range('T1')
        self.assertEqual(start, 1)
        self.assertEqual(end, 14)
        start, end = ogc_process_stages.get_process_range('T2')
        self.assertEqual(start, 15)
        self.assertEqual(end, 28)
        start, end = ogc_process_stages.get_process_range('P3')
        self.assertEqual(start, 71)
        self.assertEqual(end, 84)
        start, end = ogc_process_stages.get_process_range('P4')
        self.assertEqual(start, 85)
        self.assertEqual(end, 98)
        return
